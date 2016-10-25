******************************************************************************************

# PulsarFeatureLab

Author: Rob Lyon, School of Computer Science & Jodrell Bank Centre for Astrophysics,
		University of Manchester, Kilburn Building, Oxford Road, Manchester M13 9PL.

Contact:	rob@scienceguyrob.com or robert.lyon@postgrad.manchester.ac.uk
Web:		http://www.scienceguyrob.com or http://www.cs.manchester.ac.uk
			or alternatively http://www.jb.man.ac.uk

	:::PLEASE NOTE This is a slightly modified version of the code: the original is 
	avaliable from the sources listed above. The version included here is not guarenteed
	to remain up to date :::
******************************************************************************************

1. Overview

	The pulsar feature lab application is a collection of python scripts useful for
	extracting machine learning features (otherwise known as scores or variables) from
	pulsar candidate files. The code was written in order to provide a tool-kit useful
	for designing and extracting new candidate features, whilst retaining the ability to
	extract existing features developed by the community at large. This enables newly
	conceived features to be evaluated with respect to existing features allowing an
	objective decision on their utility to be reached.
	
	It is hoped this code base will be used by the radio astronomy community. By sharing
	features and the source code implementations used to extract them, existing and newly
	devised features can be evaluated together. A statistically optimal feature set can
	then be produced which maximises the performance of learning algorithms on observational
	data. This will assist all in isolating legitimate pulsar/transient/single-pulse
	detections in data collected around the world. Given the proliferation of observational
	data and the increase in data volumes to be expected from next generation radio telescopes
	such as the Square Kilometre Array (SKA), such collaboration is important if we are to
	avoid the `big data' problems associated with other large science projects such as the
	Atlas Experiment at the Large Hadron Collider (LHC).
	
	For more details of the toolkit please see the supplied [user guide](PFLDocumentation.pdf). 
	
	If you use the code in your work please cite us using (or see bibtex below):
	
	R. J. Lyon, B. W. Stappers, S. Cooper, J. M. Brooke, J. D. Knowles, Fifty Years of Pulsar
	Candidate Selection: From simple filters to a new principled real-time classification approach
	MNRAS, 000, p.000-000, 2015.

2. Requirements

	The pulsar feature lab scripts have the following system requirements:
	
	Python 2.4 or later.
	[SciPy](http://www.scipy.org/)
	[NumPy](http://www.numpy.org/)
	[matplotlib library] (http://matplotlib.org/)
	
2. Use
	
	The application script PulsarFeatureLab.py can be executed via:
	
	<i>python PulsarFeatureLab.py</i>
	
	The script accepts a number of arguments. It requires four of these to execute, and accepts
	another three as optional.
	
	Required Arguments
	
	Flag	Type		Description
	
	-c		integer 	Candidate file type.
	
						1. The Pulsar Hunter Candidate XML (PHCX) candidates output by the pipeline
							described by Morello et al.[6].
						2. The gnuzipped (‘.gz’) PHCX candidates produced by the pipeline described
							by Thornton [4].
						3. The prepfold (PFD) files output by the LOTAAS and similar surveys.
						
	-d      string		integer Path to the directory containing candidates.
	-f		string 		Path to the output file to create or append to.
	-t		integer		Type of features to generate.
	
						1. 12 features from Eatough et al. [2].
						2. 22 features from Bates et al. [3].
						3. 22 features from Thornton. [4].
						4. 6 features from Lee et al. [5].
						5. 6 features from Morello et al. [6].
						6. 8 features from Lyon et al. [1].
						7. Integrated (folded) profile data.
						8. DM-SNR Curve data.

	Optional Arguments
	
	Flag	Type		Description
	
	−−arff	boolean		Flag that when provided, writes feature output in the WEKA ARFF file format.
	−−meta  boolean		Flag that when provided, writes meta information, i.e. the candidate file name,
						to the output file.
	-v		boolean		Verbose debugging flag.
	
3. Citing our work

	Please use the following citation if you make use of tool:
	
	@article{Lyon:2015:bs,
	author    = {{Lyon}, R.~J. and {Stappers}, B.~W. and {Cooper}, S. and {Brooke}, J.~M. {Knowles}, J.~D.},
	title     = {{Fifty Years of Pulsar Candidate Selection: From simple filters to a new principled real-time classification approach}},
	journal   = {MNRAS},
	volume    = {000},
	year      = {2015},
	pages     = {000-000}
	}
	
4. Acknowledgements

	This work was supported by grant EP/I028099/1 for the University of Manchester Centre for
	Doctoral Training in Computer Science, from the UK Engineering and Physical Sciences Research
	Council (EPSRC).
	
6. References

	[1] R. J. Lyon et al., "Fifty Years of Pulsar Candidate Selection: From simple filters to a new
		principled real-time classification approach", Monthly Notices of the Royal Astronomical Society,
		vol. 000, no. 0, pp. 0000–0000, 2015.
		
	[2] R. P. Eatough et al., "Selection of radio pulsar candidates using artificial neural networks",
		Monthly Notices of the Royal Astronomical Society, vol. 407, no. 4, pp. 2443-2450, 2010.
		
	[3] S. D. Bates et al., "The high time resolution universe pulsar survey vi. an artificial neural
		network and timing of 75 pulsars", Monthly Notices of the Royal Astronomical Society, vol. 427,
		no. 2, pp. 1052-1065, 2012.

	[4] D. Thornton, "The High Time Resolution Radio Sky", PhD thesis, University of Manchester,
		Jodrell Bank Centre for Astrophysics School of Physics and Astronomy, 2013.
		
	[5] K. J. Lee et al., "PEACE: pulsar evaluation algorithm for candidate extraction a software package
		for post-analysis processing of pulsar survey candidates", Monthly Notices of the Royal Astronomical
		Society, vol. 433, no. 1, pp. 688-694, 2013.
		
	[6] V. Morello et al., "SPINN: a straightforward machine learning solution to the pulsar candidate
		selection problem", Monthly Notices of the Royal Astronomical Society, vol. 443, no. 2,
		pp. 1651-1662, 2014.
