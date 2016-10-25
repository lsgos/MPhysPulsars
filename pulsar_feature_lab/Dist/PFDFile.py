"""

**************************************************************************
| PFDFile.py                                                             |
**************************************************************************
| Description:                                                           |
|                                                                        |
| Represents an individual PFD candidate. This code runs on python       |
| 2.4 or later.                                                          |
**************************************************************************
| Author: Rob Lyon                                                       |
| Email : robert.lyon@postgrad.manchester.ac.uk                          |
| web   : www.scienceguyrob.com                                          |
**************************************************************************
 
"""

# Standard library Imports:
import struct, sys

# Numpy Imports:
from numpy import array
from numpy import asarray
from numpy import concatenate
from numpy import floor
from numpy import fabs
from numpy import fromfile
from numpy import reshape
from numpy import float64
from numpy import arange
from numpy import add
from numpy import mean
from numpy import zeros
from numpy import shape
from numpy import sum
from numpy import sqrt
from numpy import std

# For plotting fits etc.
import matplotlib.pyplot as plt

# Custom file Imports:
import Utilities
from PFDFeatureExtractor import PFDFeatureExtractor

# ****************************************************************************************************
#
# CLASS DEFINITION
#
# ****************************************************************************************************

class PFD(Utilities.Utilities):
    """                
    Represents an individual pulsar candidate.
    
    """
    
    # ****************************************************************************************************
    #
    # Constructor.
    #
    # ****************************************************************************************************
    
    def __init__(self,debugFlag,candidateName):
        """
        Default constructor.
        
        Parameters:
        
        debugFlag     -    the debugging flag. If set to True, then detailed
                           debugging messages will be printed to the terminal
                           during execution.
        candidateName -    the name for the candidate, typically the file path.
        """
        Utilities.Utilities.__init__(self,debugFlag)
        self.epsilon = 0.000005 # Used during feature comparison.
         
        self.cand     = candidateName
        self.features = []
        self.fe       = PFDFeatureExtractor(self.debug)
        self.load()

    # ****************************************************************************************************
           
    def load(self):
        """
        Attempts to load candidate data from the file, performs file consistency checks if the
        debug flag is set to true. Much of this code has been extracted from PRESTO by Scott Ransom.
        
        Please see:
        
        http://www.cv.nrao.edu/~sransom/presto/
        https://github.com/scottransom/presto
        
        Parameters:
        N/A
        
        Return:
        N/A
        """
        infile = open(self.cand, "rb")
        
        # The code below appears to have been taken from Presto. So it maybe
        # helpful to look at the Presto github repository (see above) to get a better feel
        # for what this code is doing. I certainly have no idea what is going on. Although
        # data is being unpacked in a specific order.
            
        swapchar = '<' # this is little-endian
        data = infile.read(5*4)
        testswap = struct.unpack(swapchar+"i"*5, data)
        # This is a hack to try and test the endianness of the data.
        # None of the 5 values should be a large positive number.
        
        if (fabs(asarray(testswap))).max() > 100000:
            swapchar = '>' # this is big-endian
            
        (self.numdms, self.numperiods, self.numpdots, self.nsub, self.npart) = struct.unpack(swapchar+"i"*5, data)
        (self.proflen, self.numchan, self.pstep, self.pdstep, self.dmstep, self.ndmfact, self.npfact) = struct.unpack(swapchar+"i"*7, infile.read(7*4))
        self.filenm = infile.read(struct.unpack(swapchar+"i", infile.read(4))[0])
        self.candnm = infile.read(struct.unpack(swapchar+"i", infile.read(4))[0])
        self.telescope = infile.read(struct.unpack(swapchar+"i", infile.read(4))[0])
        self.pgdev = infile.read(struct.unpack(swapchar+"i", infile.read(4))[0])
        
        test = infile.read(16)
        has_posn = 1
        for ii in range(16):
            if test[ii] not in '0123456789:.-\0':
                has_posn = 0
                break
            
        if has_posn:
            self.rastr = test[:test.find('\0')]
            test = infile.read(16)
            self.decstr = test[:test.find('\0')]
            (self.dt, self.startT) = struct.unpack(swapchar+"dd", infile.read(2*8))
        else:
            self.rastr = "Unknown"
            self.decstr = "Unknown"
            (self.dt, self.startT) = struct.unpack(swapchar+"dd", test)
            
        (self.endT, self.tepoch, self.bepoch, self.avgvoverc, self.lofreq,self.chan_wid, self.bestdm) = struct.unpack(swapchar+"d"*7, infile.read(7*8))
        (self.topo_pow, tmp) = struct.unpack(swapchar+"f"*2, infile.read(2*4))
        (self.topo_p1, self.topo_p2, self.topo_p3) = struct.unpack(swapchar+"d"*3,infile.read(3*8))
        (self.bary_pow, tmp) = struct.unpack(swapchar+"f"*2, infile.read(2*4))
        (self.bary_p1, self.bary_p2, self.bary_p3) = struct.unpack(swapchar+"d"*3,infile.read(3*8))
        (self.fold_pow, tmp) = struct.unpack(swapchar+"f"*2, infile.read(2*4))
        (self.fold_p1, self.fold_p2, self.fold_p3) = struct.unpack(swapchar+"d"*3,infile.read(3*8))
        (self.orb_p, self.orb_e, self.orb_x, self.orb_w, self.orb_t, self.orb_pd,self.orb_wd) = struct.unpack(swapchar+"d"*7, infile.read(7*8))
        self.dms = asarray(struct.unpack(swapchar+"d"*self.numdms,infile.read(self.numdms*8)))
        
        if self.numdms==1:
            self.dms = self.dms[0]
            
        self.periods = asarray(struct.unpack(swapchar + "d" * self.numperiods,infile.read(self.numperiods*8)))
        self.pdots = asarray(struct.unpack(swapchar + "d" * self.numpdots,infile.read(self.numpdots*8)))
        self.numprofs = self.nsub * self.npart
        
        if (swapchar=='<'):  # little endian
            self.profs = zeros((self.npart, self.nsub, self.proflen), dtype='d')
            for ii in range(self.npart):
                for jj in range(self.nsub):
                    try:
                        self.profs[ii,jj,:] = fromfile(infile, float64, self.proflen)
                    except Exception: # Catch *all* exceptions.
                        pass
                        #print ""
        else:
            self.profs = asarray(struct.unpack(swapchar+"d"*self.numprofs*self.proflen,infile.read(self.numprofs*self.proflen*8)))
            self.profs = reshape(self.profs, (self.npart, self.nsub, self.proflen))
                
        self.binspersec = self.fold_p1 * self.proflen
        self.chanpersub = self.numchan / self.nsub
        self.subdeltafreq = self.chan_wid * self.chanpersub
        self.hifreq = self.lofreq + (self.numchan-1) * self.chan_wid
        self.losubfreq = self.lofreq + self.subdeltafreq - self.chan_wid
        self.subfreqs = arange(self.nsub, dtype='d')*self.subdeltafreq + self.losubfreq
        self.subdelays_bins = zeros(self.nsub, dtype='d')
        self.killed_subbands = []
        self.killed_intervals = []
        self.pts_per_fold = []
        
        # Note: a foldstats struct is read in as a group of 7 doubles
        # the correspond to, in order:
        # numdata, data_avg, data_var, numprof, prof_avg, prof_var, redchi
        self.stats = zeros((self.npart, self.nsub, 7), dtype='d')
        
        for ii in range(self.npart):
            currentstats = self.stats[ii]
            
            for jj in range(self.nsub):
                if (swapchar=='<'):  # little endian
                    try:
                        currentstats[jj] = fromfile(infile, float64, 7)
                    except Exception: # Catch *all* exceptions.
                        pass
                        #print ""
                else:
                    try:
                        currentstats[jj] = asarray(struct.unpack(swapchar+"d"*7,infile.read(7*8)))
                    except Exception: # Catch *all* exceptions.
                        pass
                        #print ""
                    
            self.pts_per_fold.append(self.stats[ii][0][0])  # numdata from foldstats
            
        self.start_secs = add.accumulate([0]+self.pts_per_fold[:-1])*self.dt
        self.pts_per_fold = asarray(self.pts_per_fold)
        self.mid_secs = self.start_secs + 0.5*self.dt*self.pts_per_fold
        
        if (not self.tepoch==0.0):
            self.start_topo_MJDs = self.start_secs/86400.0 + self.tepoch
            self.mid_topo_MJDs = self.mid_secs/86400.0 + self.tepoch
        
        if (not self.bepoch==0.0):
            self.start_bary_MJDs = self.start_secs/86400.0 + self.bepoch
            self.mid_bary_MJDs = self.mid_secs/86400.0 + self.bepoch
            
        self.Nfolded = add.reduce(self.pts_per_fold)
        self.T = self.Nfolded*self.dt
        self.avgprof = (self.profs/self.proflen).sum()
        self.varprof = self.calc_varprof()
        self.barysubfreqs = self.subfreqs
        infile.close()
            
        # If explicit debugging required.
        if(self.debug):
            
            # If candidate file is invalid in some way...
            if(self.isValid()==False):
                
                print "Invalid PFD candidate: ",self.cand
                raise Exception("Invalid PFD candidate: PFDFile.py (Line 214).")
            
            # Candidate file is valid.
            else:
                print "Candidate file valid."
                self.profile = array(self.getprofile())
            
        # Just go directly to feature generation without checks.
        else:
            self.out( "Candidate validity checks skipped.","")
            self.profile = array(self.getprofile())
    
    # ****************************************************************************************************
    
    def getprofile(self):
        """
        Obtains the profile data from the candidate file.
        
        Parameters:
        N/A
        
        Returns:
        The candidate profile data (an array) scaled to within the range [0,255].
        """
        if not self.__dict__.has_key('subdelays'):
            self.dedisperse()
          
        normprof = self.sumprof - min(self.sumprof)
        
        s = normprof / mean(normprof)
        
        if(self.debug):
            plt.plot(s)
            plt.title("Profile.")
            plt.show()
            
        return self.scale(s)
    
    # ****************************************************************************************************
    
    def scale(self,data):
        """
        Scales the profile data for pfd files so that it is in the range 0-255.
        This is the same range used in the phcx files. So  by performing this scaling
        the features for both type of candidates are directly comparable. Before it was
        harder to determine if the features generated for pfd files were working correctly,
        since the phcx features are our only point of reference. 
        
        Parameter:
        data    -    the data to scale to within the 0-255 range.
        
        Returns:
        A new array with the data scaled to within the range [0,255].
        """
        min_=min(data)
        max_=max(data)
        
        newMin=0;
        newMax=255
        
        newData=[]
        
        for n in range(len(data)):
            
            value=data[n]
            x = (newMin * (1-( (value-min_) /( max_-min_ )))) + (newMax * ( (value-min_) /( max_-min_ ) ))
            newData.append(x)
            
        return newData
    
    # ****************************************************************************************************
        
    def calc_varprof(self):
        """
        This function calculates the summed profile variance of the current pfd file.
        Killed profiles are ignored. I have no idea what a killed profile is. But it
        sounds fairly gruesome.
        """
        varprof = 0.0
        for part in range(self.npart):
            if part in self.killed_intervals: continue
            for sub in range(self.nsub):
                if sub in self.killed_subbands: continue
                varprof += self.stats[part][sub][5] # foldstats prof_var
        return varprof
    
    # ****************************************************************************************************
        
    def dedisperse(self, DM=None, interp=0):
        """
        Rotate (internally) the profiles so that they are de-dispersed
        at a dispersion measure of DM.  Use FFT-based interpolation if
        'interp' is non-zero (NOTE: It is off by default!).
        
        """

        if DM is None:
            DM = self.bestdm
            
        # Note:  Since TEMPO pler corrects observing frequencies, for
        #        TOAs, at least, we need to de-disperse using topocentric
        #        observing frequencies.
        self.subdelays = self.fe.delay_from_DM(DM, self.subfreqs)
        self.hifreqdelay = self.subdelays[-1]
        self.subdelays = self.subdelays-self.hifreqdelay
        delaybins = self.subdelays*self.binspersec - self.subdelays_bins
        
        if interp:
            
            new_subdelays_bins = delaybins
            
            for ii in range(self.npart):
                for jj in range(self.nsub):
                    tmp_prof = self.profs[ii,jj,:]
                    self.profs[ii,jj] = self.fe.fft_rotate(tmp_prof, delaybins[jj])
                    
            # Note: Since the rotation process slightly changes the values of the
            # profs, we need to re-calculate the average profile value
            self.avgprof = (self.profs/self.proflen).sum()
            
        else:
            
            new_subdelays_bins = floor(delaybins+0.5)
            
            for ii in range(self.nsub):
                
                rotbins = int(new_subdelays_bins[ii]) % self.proflen
                if rotbins:  # i.e. if not zero
                    subdata = self.profs[:,ii,:]
                    self.profs[:,ii] = concatenate((subdata[:,rotbins:],subdata[:,:rotbins]), 1)
                    
        self.subdelays_bins += new_subdelays_bins
        self.sumprof = self.profs.sum(0).sum(0)
    
    # ******************************************************************************************
    
    def plot_chi2_vs_DM(self, loDM, hiDM, N=100, interp=0):
        """
        Plot (and return) an array showing the reduced-chi^2 versus DM 
        (N DMs spanning loDM-hiDM). Use sinc_interpolation if 'interp' is non-zero.
        """

        # Sum the profiles in time
        sumprofs = self.profs.sum(0)
        
        if not interp:
            profs = sumprofs
        else:
            profs = zeros(shape(sumprofs), dtype='d')
            
        DMs = self.fe.span(loDM, hiDM, N)
        chis = zeros(N, dtype='f')
        subdelays_bins = self.subdelays_bins.copy()
        
        for ii, DM in enumerate(DMs):
            
            subdelays = self.fe.delay_from_DM(DM, self.barysubfreqs)
            hifreqdelay = subdelays[-1]
            subdelays = subdelays - hifreqdelay
            delaybins = subdelays*self.binspersec - subdelays_bins
            
            if interp:
                
                interp_factor = 16
                for jj in range(self.nsub):
                    profs[jj] = self.fe.interp_rotate(sumprofs[jj], delaybins[jj],zoomfact=interp_factor)
                # Note: Since the interpolation process slightly changes the values of the
                # profs, we need to re-calculate the average profile value
                avgprof = (profs/self.proflen).sum()
                
            else:
                
                new_subdelays_bins = floor(delaybins+0.5)
                for jj in range(self.nsub):
                    profs[jj] = self.fe.rotate(profs[jj], int(new_subdelays_bins[jj]))
                subdelays_bins += new_subdelays_bins
                avgprof = self.avgprof
                
            sumprof = profs.sum(0)        
            chis[ii] = self.calc_redchi2(prof=sumprof, avg=avgprof)

        return (chis, DMs)
    
    # ******************************************************************************************
    
    def calc_redchi2(self, prof=None, avg=None, var=None):
        """
        Return the calculated reduced-chi^2 of the current summed profile.
        """
        
        if not self.__dict__.has_key('subdelays'):
            self.dedisperse()
            
        if prof is None:  prof = self.sumprof
        if avg is None:  avg = self.avgprof
        if var is None:  var = self.varprof
        return ((prof-avg)**2.0/var).sum()/(len(prof)-1.0)
    
    # ******************************************************************************************
    
    def plot_subbands(self):
        """
        Plot the interval-summed profiles vs subband.  Restrict the bins
        in the plot to the (low:high) slice defined by the phasebins option
        if it is a tuple (low,high) instead of the string 'All'. 
        """
        if not self.__dict__.has_key('subdelays'):
            self.dedisperse()
        
        lo, hi = 0.0, self.proflen
        profs = self.profs.sum(0)
        lof = self.lofreq - 0.5*self.chan_wid
        hif = lof + self.chan_wid*self.numchan
        
        return profs
                        
    # ****************************************************************************************************
        
    def isValid(self):
        """
        Tests the data loaded from a pfd file.
        
        Parameters:
        
        Returns:
        True if the data is well formed and valid, else false.
        """
        
        # These are only basic checks, more in depth checks should be implemented
        # by someone more familiar with the pfd file format.
        if(self.proflen > 0 and self.numchan > 0):
            return True
        else:
            return False
        
    # ****************************************************************************************************
    
    def computeFeatures(self,feature_type):
        """
        Builds the features using FeatureExtractor.py and PFDFeatureExtractor.py 
        source files. Returns the features.
        
        Parameters:
        type               -    the type of features to generate.
        
                                feature_type = 1 generates 12 features from Eatough et al., MNRAS, 407, 4, 2010.
                                feature_type = 2 generates 22 features from Bates et al., MNRAS, 427, 2, 2012.
                                feature_type = 3 generates 22 features from Thornton, PhD Thesis, Univ. Manchester, 2013.
                                feature_type = 4 generates 6 features from Lee et al., MNRAS, 333, 1, 2013.
                                feature_type = 5 generates 6 features from Morello et al., MNRAS, 433, 2, 2014.
                                feature_type = 6 generates 8 features from Lyon et al.,2015.
                                feature_type = 7 obtains raw integrated (folded) profile data.
                                feature_type = 8 obtains raw DM-SNR Curve data.
        
        Returns:
        An array of candidate features as floating point values.
        """
        
        if(feature_type == 1):
            return self.computeType_1()
        elif(feature_type == 2):
            return self.computeType_2()
        elif(feature_type == 3):
            return self.computeType_3()
        elif(feature_type == 4):
            return self.computeType_4()
        elif(feature_type == 5):
            return self.computeType_5()
        elif(feature_type == 6):
            return self.computeType_6()
        elif(feature_type == 7):
            return self.computeType_7()
        elif(feature_type == 8):
            return self.computeType_8()
        # ADDING A NEW FEATURE? Add a new call here to self.computeType_<your function number>()
        else:
            raise Exception("Invalid features specified!")
            
    # ****************************************************************************************************
    
    def computeType_1(self):
        """
        Generates 12 features from Eatough et al., MNRAS, 407, 4, 2010.
        
        Parameters:
        N/A
        
        Returns:
        An array of 12 candidate features as floating point values.
        """
        
        # The features described in this work have not been implemented.
        # It is hoped the authors of this work, or others, will implement the features
        # at some point, allowing for a full comparison between all features.
        #
        # Please add PHCX and PFD compatible feature extraction code for this work in
        # FeatureExtractor.py     - for code that applies to both PHXC and PFD files.
        # PHCXFeatureExtractor.py - for code that applies to PHXC files only.
        # PFDFeatureExtractor.py  - for code that applies to PFD files only.
        
        for count in range(1,23):
            self.features.append(0.0)
         
        return self.features
    
    # ****************************************************************************************************
    
    def computeType_2(self):
        """
        Generates 22 features from Bates et al., MNRAS, 427, 2, 2012.
        
        Parameters:
        N/A
        
        Returns:
        An array of 22 candidate features as floating point values.
        """
        
        # The features described in this work have not been implemented.
        # It is hoped the authors of this work, or others, will implement the features
        # at some point, allowing for a full comparison between all features.
        #
        # Please add PHCX and PFD compatible feature extraction code for this work in
        # FeatureExtractor.py     - for code that applies to both PHXC and PFD files.
        # PHCXFeatureExtractor.py - for code that applies to PHXC files only.
        # PFDFeatureExtractor.py  - for code that applies to PFD files only.
        
        for count in range(1,23):
            self.features.append(0.0)
            
        return self.features
    
    # ****************************************************************************************************    
    def computeType_3(self):
        """
        Generates 22 features from Thornton, PhD Thesis, Univ. Manchester, 2013.
        
        Features:
        
        Computes the sinusoid fitting features for the profile data. There are four features computed:
        
        Feature 1. Chi-Squared value for sine fit to raw profile. This attempts to fit a sine curve
                 to the pulse profile. The reason for doing this is that many forms of RFI are sinusoidal.
                 Thus the chi-squared value for such a fit should be low for RFI (indicating
                 a close fit) and high for a signal of interest (indicating a poor fit).
                 
        Feature 2. Chi-Squared value for sine-squared fit to amended profile. This attempts to fit a sine
                 squared curve to the pulse profile, on the understanding that a sine-squared curve is similar
                 to legitimate pulsar emission. Thus the chi-squared value for such a fit should be low for
                 RFI (indicating a close fit) and high for a signal of interest (indicating a poor fit).
                 
        Feature 3. Difference between maxima. This is the number of peaks the program identifies in the pulse
                 profile - 1. Too high a value may indicate that a candidate is caused by RFI. If there is only
                 one pulse in the profile this value should be zero.
                 
        Feature 4. Sum over residuals.  Given a pulse profile represented by an array of profile intensities P,
                 the sum over residuals subtracts ( (max-min) /2) from each value in P. A larger sum generally
                 means a higher SNR and hence other features will also be stronger, such as correlation between
                 sub-bands. Example,
                 
                 P = [ 10 , 13 , 17 , 50 , 20 , 10 , 5 ]
                 max = 50
                 min = 5
                 (abs(max-min))/2 = 22.5
                 so the sum over residuals is:
                 
                  = (22.5 - 10) + (22.5 - 13) + (22.5 - 17) + (22.5 - 50) + (22.5 - 20) + (22.5 - 10) + (22.5 - 5)
                  = 12.5 + 9.5 + 5.5 + (-27.5) + 2.5 + 12.5 + 17.5
                  = 32.5
        
        Computes the Gaussian fitting features for the profile data. There are seven features computed:
        
        Feature 5. Distance between expectation values of Gaussian and fixed Gaussian fits to profile histogram.
                 This fits a two Gaussian curves to a histogram of the profile data. One of these
                 Gaussian fits has its mean value set to the value in the centre bin of the histogram,
                 the other is not constrained. Thus it is expected that for a candidate arising from noise,
                 these two fits will be very similar - the distance between them will be zero. However a
                 legitimate signal should be different giving rise to a higher feature value.
                 
        Feature 6. Ratio of the maximum values of Gaussian and fixed Gaussian fits to profile histogram.
                 This computes the maximum height of the fixed Gaussian curve (mean fixed to the centre
                 bin) to the profile histogram, and the maximum height of the non-fixed Gaussian curve
                 to the profile histogram. This ratio will be equal to 1 for perfect noise, or close to zero
                 for legitimate pulsar emission.
        
        Feature 7. Distance between expectation values of derivative histogram and profile histogram. A histogram
                 of profile derivatives is computed. This finds the absolute value of the mean of the 
                 derivative histogram, minus the mean of the profile histogram. A value close to zero indicates 
                 a candidate arising from noise, a value greater than zero some form of legitimate signal.
        
        Feature 8. Full-width-half-maximum (FWHM) of Gaussian fit to pulse profile. Describes the width of the
                 pulse, i.e. the width of the Gaussian fit of the pulse profile. Equal to 2*sqrt( 2 ln(2) )*sigma.
                 Not clear whether a higher or lower value is desirable.
        
        Feature 9. Chi squared value from Gaussian fit to pulse profile. Lower values are indicators of a close fit,
                 and a possible profile source.
        
        Feature 10. Smallest FWHM of double-Gaussian fit to pulse profile. Some pulsars have a doubly peaked
                  profile. This fits two Gaussians to the pulse profile, then computes the FWHM of this
                  double Gaussian fit. Not clear if higher or lower values are desired.
        
        Feature 11. Chi squared value from double Gaussian fit to pulse profile. Smaller values are indicators
                  of a close fit and possible pulsar source.
        
        Computes the candidate parameters. There are four features computed:
        
        Feature 12. The candidate period.
                 
        Feature 13. The best signal-to-noise value obtained for the candidate. Higher values desired.
        
        Feature 14. The best dispersion measure (dm) obtained for the candidate. Low DM values 
                  are assocaited with local RFI.
                 
        Feature 15. The best pulse width.
        
        Computes the dispersion measure curve fitting parameters:
        
        Feature 16. This feature computes SNR / SQRT( (P-W) / W ).
                 
        Feature 17. Difference between fitting factor Prop, and 1. If the candidate is a pulsar,
                  then prop should be equal to 1.
        
        Feature 18. Difference between best DM value and optimised DM value from fit. This difference
                  should be small for a legitimate pulsar signal. 
                 
        Feature 19. Chi squared value from DM curve fit, smaller values indicate a smaller fit. Thus
                  smaller values will be possessed by legitimate signals.
        
         Computes the sub-band features:
        
        Feature 20. RMS of peak positions in all sub-bands. Smaller values should be possessed by
                  legitimate pulsar signals.
                 
        Feature 21. Average correlation coefficient for each pair of sub-bands. Larger values should be
                  possessed by legitimate pulsar signals.
        
        Feature 22. Sum of correlation coefficients between sub-bands and profile. Larger values should be
                  possessed by legitimate pulsar signals.
                  
        Parameters:
        N/A
        
        Returns:
        An array of 22 candidate features as floating point values.
        """
        
        # Get features 1-4
        try:
            sin_fit = self.fe.getSinusoidFittings(self.profile)
            # Add first features.
            self.features.append(float(sin_fit[0])) # Feature 1.  Chi-Squared value for sine fit to raw profile.
            self.features.append(float(sin_fit[1])) # Feature 2.  Chi-Squared value for sine-squared fit to amended profile.
            self.features.append(float(sin_fit[2])) # Feature 3.  Difference between maxima.
            self.features.append(float(sin_fit[3])) # Feature 4.  Sum over residuals.
            
            if(self.debug==True):
                print "\nFeature 1. Chi-Squared value for sine fit to raw profile = ",sin_fit[0]
                print "Feature 2. Chi-Squared value for sine-squared fit to amended profile = ",sin_fit[1]
                print "Feature 3. Difference between maxima = ",sin_fit[2]
                print "Feature 4. Sum over residuals = ",sin_fit[3]
        
        # Get features 5-11
            guassian_fit = self.fe.getGaussianFittings(self.profile)
            
            self.features.append(float(guassian_fit[0]))# Feature 5. Distance between expectation values of Gaussian and fixed Gaussian fits to profile histogram.
            self.features.append(float(guassian_fit[1]))# Feature 6. Ratio of the maximum values of Gaussian and fixed Gaussian fits to profile histogram.
            self.features.append(float(guassian_fit[2]))# Feature 7. Distance between expectation values of derivative histogram and profile histogram.
            self.features.append(float(guassian_fit[3]))# Feature 8. Full-width-half-maximum (FWHM) of Gaussian fit to pulse profile. 
            self.features.append(float(guassian_fit[4]))# Feature 9. Chi squared value from Gaussian fit to pulse profile.
            self.features.append(float(guassian_fit[5]))# Feature 10. Smallest FWHM of double-Gaussian fit to pulse profile. 
            self.features.append(float(guassian_fit[6]))# Feature 11. Chi squared value from double Gaussian fit to pulse profile.
            
            if(self.debug==True):
                print "\nFeature 5. Distance between expectation values of Gaussian and fixed Gaussian fits to profile histogram = ", guassian_fit[0]
                print "Feature 6. Ratio of the maximum values of Gaussian and fixed Gaussian fits to profile histogram = ",guassian_fit[1]
                print "Feature 7. Distance between expectation values of derivative histogram and profile histogram. = ",guassian_fit[2]
                print "Feature 8. Full-width-half-maximum (FWHM) of Gaussian fit to pulse profile = ", guassian_fit[3]
                print "Feature 9. Chi squared value from Gaussian fit to pulse profile = ",guassian_fit[4]
                print "Feature 10. Smallest FWHM of double-Gaussian fit to pulse profile = ", guassian_fit[5]
                print "Feature 11. Chi squared value from double Gaussian fit to pulse profile = ", guassian_fit[6]
        

        # Get features 12-15
            candidateParameters = self.fe.getCandidateParameters(self)
            
            self.features.append(float(candidateParameters[0]))# Feature 12. Best period.
            self.features.append(self.filterFeature(13,float(candidateParameters[1])))# Feature 13. Best S/N value.
            self.features.append(self.filterFeature(14,float(candidateParameters[2])))# Feature 14. Best DM value.
            self.features.append(float(candidateParameters[3]))# Feature 15. Best pulse width.
            
            if(self.debug==True):
                print "\nFeature 12. Best period = "         , candidateParameters[0]
                print "Feature 13. Best S/N value = "        , candidateParameters[1], " Filtered value = ", self.filterFeature(13,float(candidateParameters[1]))
                print "Feature 14. Best DM value = "         , candidateParameters[2], " Filtered value = ", self.filterFeature(14,float(candidateParameters[2]))
                print "Feature 15. Best pulse width = "      , candidateParameters[3]
        
        # Get features 16-19        
            DMCurveFitting = self.fe.getDMFittings(self)
            
            self.features.append(float(DMCurveFitting[0]))# Feature 16. SNR / SQRT( (P-W)/W ).
            self.features.append(float(DMCurveFitting[1]))# Feature 17. Difference between fitting factor, Prop, and 1.
            self.features.append(self.filterFeature(18,float(DMCurveFitting[2])))# Feature 18. Difference between best DM value and optimised DM value from fit, mod(DMfit - DMbest).
            self.features.append(float(DMCurveFitting[3]))# Feature 19. Chi squared value from DM curve fit.
            
            if(self.debug==True):
                print "\nFeature 16. SNR / SQRT( (P-W) / W ) = " , DMCurveFitting[0]
                print "Feature 17. Difference between fitting factor, Prop, and 1 = " , DMCurveFitting[1]
                print "Feature 18. Difference between best DM value and optimised DM value from fit, mod(DMfit - DMbest) = ", DMCurveFitting[2], " Filtered value = ", self.filterFeature(18,float(DMCurveFitting[2]))
                print "Feature 19. Chi squared value from DM curve fit = " , DMCurveFitting[3]
        
        
        # Get features 20-22
            subbandFeatures = self.fe.getSubbandParameters(self,self.profile)
            
            self.features.append(float(subbandFeatures[0]))# Feature 20. RMS of peak positions in all sub-bands.
            self.features.append(float(subbandFeatures[1]))# Feature 21. Average correlation coefficient for each pair of sub-bands.
            self.features.append(float(subbandFeatures[2]))# Feature 22. Sum of correlation coefficients between sub-bands and profile.
            
            if(self.debug==True):
                print "\nFeature 20. RMS of peak positions in all sub-bands = " , subbandFeatures[0]
                print "Feature 21. Average correlation coefficient for each pair of sub-bands = " , subbandFeatures[1]
                print "Feature 22. Sum of correlation coefficients between sub-bands and profile = " , subbandFeatures[2]
        
        except Exception as e: # catch *all* exceptions
            print "Error computing features \n\t", sys.exc_info()[0]
            print self.format_exception(e)
            raise Exception("Exception computing 22 features from Thornton, PhD Thesis, Univ. Manchester, 2013.")
        
        return self.features
    
    # ****************************************************************************************************
    
    def computeType_4(self):
        """
        Generates 6 features from Lee et al., MNRAS, 333, 1, 2013.
        
        Parameters:
        N/A
        
        Returns:
        An array of 6 candidate features as floating point values.
        """
        
        # The features described in this work have not been implemented.
        # It is hoped the authors of this work, or others, will implement the features
        # at some point, allowing for a full comparison between all features.
        #
        # Please add PHCX and PFD compatible feature extraction code for this work in
        # FeatureExtractor.py     - for code that applies to both PHXC and PFD files.
        # PHCXFeatureExtractor.py - for code that applies to PHXC files only.
        # PFDFeatureExtractor.py  - for code that applies to PFD files only.
        
        for count in range(1,7):
            self.features.append(0.0)
    
        return self.features
    
    # ****************************************************************************************************
    
    def computeType_5(self):
        """
        Generates 6 features from Morello et al., MNRAS, 433, 2, 2014.
        
        Parameters:
        N/A
        
        Returns:
        An array of 6 candidate features as floating point values.
        """
        
        # The features described in this work have not been implemented.
        # It is hoped the authors of this work, or others, will implement the features
        # at some point, allowing for a full comparison between all features.
        #
        # Please add PHCX and PFD compatible feature extraction code for this work in
        # FeatureExtractor.py     - for code that applies to both PHXC and PFD files.
        # PHCXFeatureExtractor.py - for code that applies to PHXC files only.
        # PFDFeatureExtractor.py  - for code that applies to PFD files only.
        
        for count in range(1,7):
            self.features.append(0.0)
    
        return self.features
    
    # ****************************************************************************************************
    
    def computeType_6(self):
        """
        Generates 8 features from Lyon et al.,2015.
        
        Feature 1. Mean of the integrated (folded) pulse profile.
        Feature 2. Standard deviation of the integrated (folded) pulse profile.
        Feature 3. Skewness of the integrated (folded) pulse profile.
        Feature 4. Excess kurtosis of the integrated (folded) pulse profile.
        Feature 5. Mean of the DM-SNR curve.
        Feature 6. Standard deviation of the DM-SNR curve.
        Feature 7. Skewness of the DM-SNR curve.
        Feature 8. Excess kurtosis of the DM-SNR curve.
        
        Parameters:
        N/A
        
        Returns:
        An array of 8 candidate features as floating point values.
        """
        try:
            
            # First compute profile stats.
            bins = [] 
            
            for intensity in self.profile:
                bins.append(float(intensity))
            
            mn = mean(bins)
            stdev = std(bins)
            skw = self.fe.skewness(bins)         
            kurt = self.fe.excess_kurtosis(bins) 
            
            if(self.debug==True):
                print "\nFeature 1. Mean of the integrated (folded) pulse profile = ",            str(mn)
                print "Feature 2. Standard deviation of the integrated (folded) pulse profile = ",str(stdev)
                print "Feature 3. Skewness of the integrated (folded) pulse profile = ",          str(skw)
                print "Feature 4. Excess Kurtosis of the integrated (folded) pulse profile = ",   str(kurt)
                
            self.features.append(mn)
            self.features.append(stdev)
            self.features.append(skw)
            self.features.append(kurt)
            
            # Now compute DM-SNR curve stats.
            bins =[]
            bins = self.fe.getDMCurveData(self)
            
            mn = mean(bins)
            stdev = std(bins)
            skw = self.fe.skewness(bins)         
            kurt = self.fe.excess_kurtosis(bins)
            
            if(self.debug==True):
                print "\nFeature 5. Mean of the integrated SNR-DM Curve = ", str(mn)
                print "Feature 6. Standard deviation of the SNR-DM Curve = ",str(stdev)
                print "Feature 7. Skewness of the SNR-DM Curve = ",          str(skw)
                print "Feature 8. Excess Kurtosis of the SNR-DM Curve = ",   str(kurt)
                
            self.features.append(mn)
            self.features.append(stdev)
            self.features.append(skw)
            self.features.append(kurt) 
            
        except Exception as e: # catch *all* exceptions
            print "Error getting features from PFD file\n\t", sys.exc_info()[0]
            print self.format_exception(e)
            raise Exception("Exception computing 8 features from Lyon et al.,2015.")
        
        return self.features

    # ****************************************************************************************************
    
    def computeType_7(self):
        """
        Obtain integrated (folded profile data.
        
        Parameters:
        N/A
        
        Returns:
        An array of data.
        """
        
        for intensity in self.profile:
            self.features.append(float(intensity))
            
        return self.features
        
    # ****************************************************************************************************
    
    def computeType_8(self):
        """
        Obtain SNR-DM curve data.
        Parameters:
        N/A
        
        Returns:
        An array of data.
        """
        
        curve = self.fe.getDMCurveData(self)
            
        return curve   
    
    # ADDING A NEW FEATURE? - declare a new function computeType_<your feature type>() that
    # calculates and extracts your feature values.
    
    # ******************************************************************************************
    
    def filterFeature(self,s,value):
        """
        Filters a return feature value, so that if it is outside an expected range,
        then the feature is corrected, and the corrected version returned.
        
        Parameter:
        s        -    index of the feature, i.e. 1,2,3,...,n.
        value    -    the value of the feature.
        
        Return:
        The feature value if it is valid, else a formatted version of the feature.
        """

        if(s==13):# SNR
            if(self.isEqual(value, 0.0, self.epsilon)==-1):
                return 0.0
            else:
                return value
            
        elif(s==14): # DM
            if(self.isEqual(value, 0.0, self.epsilon)==-1):
                return 0.0
            else:
                return value
            
        elif(s==18): # mod(DMfit - DMbest).
            return float(abs(value))
        else:
            return value
    
    # ******************************************************************************************
    
    def isEqual(self,a,b,epsln):
        """
        Used to compare two floats for equality. This code has to cope with some
        extreme possibilities, i.e. the comparison of two floats which are arbitrarily
        small or large.
        
        Parameters:
        a        -    the first floating point number.
        b        -    the second floating point number.
        epsln    -    the allowable error.
        
        Returns:
        
        A value of -1 if a < b, a value greater than 1 if a > b, else
        zero is returned.
        
        """
        
        # There are two possibilities - both numbers may have exponents,
        # neither may have exponents, or a combination may occur. We need
        # a valid way to compare numbers with these possibilities which fits
        # ALL scenarios. The decision here (right or wrong!) is to avoid
        # wasting time on the perfect solution, and just allow the user to
        # specify an epsilon value they are happy with. In this case we 
        # are assuming a change to the feature smaller than epsilon is 
        # effectively meaningless. 
        
        if( abs(a - b) > epsln):
            if( a < b):
                return -1
            else:
                return 1 
        else:
            return 0
    
    # *******************************************************************************************