import numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy import units
import os

MPHYS_ROOT = os.environ['MPHYSPULSARS']

MISSING_DATA_FILL_VALUE = '__ASDF__'

def _get_cols(use_all=False):
    if use_all:
        cols = Table.read('psrcat.columns', format='ascii.fixed_width')['name']
        cols = ' '.join(cols)
    else:
        cols = 'PSRJ PSRB NAME '
        cols += 'RAJ DECJ PMRA PMDEC RAJD DECJD GL GB PML PMB '
        cols += 'DM P0 P1 BINARY DIST_DM DIST_DM1 DIST_AMN DIST_AMX '
        cols += 'DIST_A DIST DIST1 RADDIST '
        cols += 'SURVEY ASSOC TYPE DATE OSURVEY '
        cols += 'AGE AGE_I BSURF_I EDOT_I EDOTD2 PMTOT VTRANS BSURF B_LC EDOT'

    return cols.split()

def get_psrcat_table():
    cols = _get_cols()
    table = Table.read(os.path.join(MPHYS_ROOT,'psrcat_tar','psrcat.ascii'), format='ascii.basic',
               names=cols, guess=False,
               fill_values=[(MISSING_DATA_FILL_VALUE, '0')],
    )

    # Add useful extra columns
    pos = SkyCoord(table['RAJD'], table['DECJD'], unit='deg')
    table['RAJ2000'] = pos.ra.to('deg')
    table['DEJ2000'] = pos.dec.to('deg')
    table['GLON'] = pos.galactic.l.to('deg')
    table['GLAT'] = pos.galactic.b.to('deg')

    table.rename_column('NAME', 'Source_Name')
    return table

def get_coord_catalog(table):
	decs =np.array(table['DECJ'])
	ras = np.array(table['RAJ'])
	catalog = [" ".join([ra,dec]) for ra,dec in zip(ras,decs)]	
	return SkyCoord(catalog, unit = (units.deg, units.deg))

PSRCAT_TABLE = get_psrcat_table()
PSRCAT = get_coord_catalog(PSRCAT_TABLE)



def return_match(skycoord, min_sep):
	index, sep, dist = skycoord.match_to_catalog_sky(PSRCAT,1)
	if sep[0] > min_sep: #sep is an array
		return None, None
	else:
		entry = PSRCAT_TABLE[index[()]] 
		return get_entry_info(entry), entry
		#index is a 'zero dimensional' array, requireing this odd syntax to get the actual number
	

def get_entry_info(entry):
	"""
	returns useful information from the psrcat table entry: the period and the dm are the most useful 
	for the purposes of matching the candidates
	"""
	dm = float(entry['DM'])
	p0 = float(entry['P0']) * 1000 #convert to ms 
	
	return {'DM' : dm, 'P0_ms': p0} 