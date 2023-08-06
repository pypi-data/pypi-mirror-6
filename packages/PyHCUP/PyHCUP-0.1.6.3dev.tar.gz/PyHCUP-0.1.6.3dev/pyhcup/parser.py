"""Read in and process data from HCUP (and Texas PUDF)
"""
import re
import os
import numpy
import pandas as pd
from pandas import DataFrame

# save a little overhead on dispatch for these later
na_value = numpy.NaN
re_match = re.match



"""Lots of local config stuff"""
# pathing information to reach bundled utilization flag definitions
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
BUNDLED_UFLAGDEF = os.path.join(dir_path, 'data', 'uflags', 'uflag_definitions.csv')


# definitions for replacing missing values down the line
MISSING_PATTERNS = {
        'missing':        '-9*\.?9*[^-\.]| |\.',
        'invalid':        '-8*\.?8*[^-\.]|A',
        'unavailable':    '-7*\.?7*[^-\.]',
        'inconsistent':   '-6*\.?6*[^-\.]',
        'notapplicable':  '-5*\.?5*[^-\.]',
        'tx_cell_too_sm': '-?999+8',
        'tx_invalid':     '\*',
        'tx_missing':     '\.|`',
        }

# pre-compile for later use, or for accessing this via dot notation
# e.g. from pyhcup.parser import COMPILED_MISSING_PATTERNS
COMPILED_MISSING_PATTERNS = re.compile('^%s$' % '|'.join(MISSING_PATTERNS.values()))


# configuration of maps for converting wide to long
# TODO: these should probably be made into actual objects of some kind
# given especially that later on down the line db.long_table_sql() has
# config-y stuff in it that might be useful outside of that function alone
LONG_MAPS = {
    'CHGS': {
        'CHARGE': ['CHG', 'REVCHG'],
        'RATE': ['RATE'],
        'REVCODE': ['REVCD'],
        'UNITS': ['UNIT'],
    },
    'DX': {
        'DX': ['DX'],
        'DXCCS': ['DXCCS'],
        'DXPOA': ['DXPOA'],
        'DXV': ['DXV'],
        # WARNING: DxatAdmit and TMDX need to be consolidated into DXPOA.
        # This will require a mapping definition, which should probably be written
        # into PyHCUP given the huge pile of data that will be affected.
        # alternatively, these could stay in their own columns in a long table
        # definition and be accessed intelligently (!) from there.
        'DXatAdmit': ['DXatAdmit'],
        'TMDX': ['TMDX'],
        
    },
    'PR': {
        'PR': ['PR'],
        'PRCCS': ['PRCCS'],
        'PRDATE': ['PRDATE'],
        'PRDAY': ['PRDAY'],
        'PRMONTH': ['PRMONTH'],
        'PRYEAR': ['PRYEAR'],
        'PRMCCS': ['PRMCCS'],
        'PRV': ['PRV'],
        'PCLASS': ['PCLASS'],
    },
}


def read(target, meta_df=None, state=None, year=None, variety=None,
         skiprows=None, nrows=None, chunksize=None):
    """Read in target data file. Uses supplied meta_df or infers from state, year, variety.
    
    Returns a pandas DataFrame object containing the parsed data if chunksize is None, otherwise returns a reader generating chunksize chunks with each iteration.
    
    target -> required
        1. full path to a data file (including filename); or
        2. a file-like Python object (e.g. handler)
    
    meta_df -> optional
        may be a pandas DataFrame object containing meta data (width and field)
    
    Can optionally specify rows to skip (skiprows) or limit the number of rows to read (nrows).
    """
    import pandas as pd
    from pyhcup import meta
    
    if meta_df is not None:
        assert type(meta_df) is pd.DataFrame, "If used, meta_df must be a pandas DataFrame object"
        assert 'width' in meta_df.columns, "meta_df DataFrame must contain a column 'width'"
        assert 'field' in meta_df.columns, "meta_df DataFrame must contain a column 'field'"
    else:
        #need to try to look up a load file
        assert type(state) is str, "state must be a string if not supplying meta"
        assert type(year) is str or type(year) is int, "year must be a string or integer if not supplying meta"
        assert type(variety) is str, "variety must be a string if not supplying meta"
        meta_df = meta.get(state, year, variety)
    
    widths = [int(x) for x in meta_df.width]
    names = [x for x in meta_df.field]
    
    result = pd.read_fwf(target, header=None, widths=widths, names=names,
                         nrows=nrows, skiprows=skiprows, chunksize=chunksize)
    return result


def replace_sentinels(df, extra_dict=None):
    """Replaces sentinel patterns and values for bad data
    
    HCUP definitions from http://www.hcup-us.ahrq.gov/db/coding.pdf
    TX PUDF definitions from individual year manuals http://www.dshs.state.tx.us/thcic/hospitals/Inpatientpudf.shtm
    """
    
    df = df.applymap(
        lambda x: na_value if re_match(COMPILED_MISSING_PATTERNS, str(x)) is not None else x
        )
    return df


def replace_df_placeholders(df, extra_dict=None):
    dictionary = {'Y': 1, 'N': 0}
    if extra_dict is not None:
        dictionary.update(extra_dict)
        
    df = df.applymap(lambda x: dictionary.get(x) if x in dictionary else x)
    return df


class UtilizationFlagger:
    def __init__(self, uflag_name, revcodes=None, pr=None, prccs=None):
        """Object holding a definition for a utilization flag. Can also apply the definition to a set of charges and procedures data in order to determine the appropriate value for the utilization flag. Must specify at least one of revcodes, pr, and prccs.
        
        Parameters
        revcodes: list (optional)
            Contains a list of UB92/UB04 revenue codes associated with the utilitzation flag. Must contain codes as integers
        
        pr: list (optional)
            Contains a list of ICD-9-CM procedure codes associated with the utilitzation flag. Must contain codes as integers.
        
        prccs: list (optional)
            Contains a list of Clinical Classification Software (CCS) procedure codes associated with the utilization flag. Must contain codes as integers.
        """
        # save passed parameters
        self.name = uflag_name
        self.revcodes = revcodes
        self.pr = pr
        self.prccs = prccs
        
        # validation of passed parameters
        if (
            not isinstance(revcodes, list) and
            not isinstance(pr, list) and
            not isinstance(prccs, list)
            ):
            raise Exception("At least one of revcodes, pr, and prccs must be a list")
        
        if not isinstance(uflag_name, str):
            raise Exception("uflag_name must be a string (got %s)" % type(uflag_name))
        
        for v in ['revcodes', 'pr', 'prccs']:
            a = getattr(self, v)
            if a is not None and not isinstance(a, list):
                raise Exception("%s must be None or a list" % v)
            elif isinstance(a, list):
                try:
                    setattr(self, '_' + v, [int(i) for i in a] + [str(i) for i in a])
                except:
                    raise Exception("If %s is a list, it can only contain integers" % v)
            else:
                setattr(self, '_' + v, [])
    
    
    def __repr__(self):
        return "<UtilizationFlagger: %s>" % self.name
    
    
    def apply(self, record_id, chgs_df, pr_df):
        """Searches procedures and charges to determine whether the indicated record_id should have this particular utilization flag. Returns the appropriate value based on HCUP flag coding conventions.
        
        Parameters

        pr_df: pandas DataFrame, required
            Procedure data in long format (indexed on KEY, data are ICD-9 codes in column PR and CCS codes in column PRCCS)

        chgs_df: pandas DataFrame, required
            Charges data in long format (indexed on KEY, data are UB92/UB04 codes in column REVCODE [and dollar amounts in CHARGE?])
        
        Return values:
            0: Neither procedures nor charges support this flag.
            1: Charges support this flag, but procedures do not.*
            2: Procedures support this flag, but charges do not.*
            3: Both charges and procedures suppor this flag.

            *N.B. that this does not mean that contradictory information is present, only that one category of information lacks positive evidence in support of the utilization flag.
        """
        
        # default values
        flag = 0
        chgs_match = False
        pr_match = False

        if chgs_df is not None and record_id in chgs_df.index.values:
            # some charges exist for this record_id
            # search them
            
            chgs_search = chgs_df.ix[record_id]
            
            # a hack because index searches return Series for single matches
            if isinstance(chgs_search, pd.Series):
                chgs_search = DataFrame(chgs_search).T
            
            check_match = chgs_search[ chgs_search.REVCODE.isin(self._revcodes) ]
            #print "REVCODE in %s: %s time(s)" % (self._revcodes, len(check_match))
            if len(check_match) > 0:
                chgs_match = True
        
        if pr_df is not None and record_id in pr_df.index.values:
            # some procedures exist for this record_id
            # search them

            pr_search = pr_df.ix[record_id]
            
            # a hack because index searches return Series for single matches
            if isinstance(pr_search, pd.Series):
                #print "Got a Series object for searched procedures"
                #print pr_search
                
                pr_search = DataFrame(pr_search).T
                #print "converted procedures:"
                #print pr_search
            
            if pr_match == False: # only search codes if haven't found a match yet
                check_match = pr_search[ pr_search.PR.isin(self._pr) ]
                #print "PR in %s: %s time(s)" % (self._pr, len(check_match))
                if len(check_match) > 0:
                    pr_match = True

            if pr_match == False: # only search codes if haven't found a match yet
                check_match = pr_search[ pr_search.PRCCS.isin(self._prccs) ]
                #print "PRCCS in %s: %s time(s)" % (self._prccs, len(check_match))
                if len(check_match) > 0:
                    pr_match = True
        
        if chgs_match is True:
            if pr_match is True:
                flag = 3
            else:
                flag = 1
        elif pr_match is True:
            flag = 2
        else:
            flag = 0
       
        return flag


def default_uflaggers():
    """Creates a list of UtilizationFlagger objects using the default utilization flag definitions bundled in PyHCUP
    """
    definitions = pd.read_csv(BUNDLED_UFLAGDEF)
    
    flaggers = []
    for k, d in definitions.iterrows():
        if pd.isnull(d['revcodes']):
            r = None
        else:
            r = d['revcodes'].split(';')
        
        if pd.isnull(d['pr']):
            pr = None
        else:
            pr = d['pr'].split(';')
        
        if pd.isnull(d['prccs']):
            prccs = None
        else:
            prccs = d['prccs'].split(';')
        
        
        f = UtilizationFlagger(d['name'], revcodes=r, pr=pr, prccs=prccs)
        flaggers.append(f)
    
    return flaggers


def parse_wide_label(wide_label, category='CHGS'):
    """Breaks a wide format column label from a charges record into its component pieces.
    """
    
    if category in LONG_MAPS.keys():
        long_map = LONG_MAPS[category]
    else:
        raise Exception("parse_wide_label() was called with category %s, but that category does not exist in LONG_MAPS (valid values are %s)" % (category, LONG_MAPS.keys()))
    
    type_re_pattern='(?P<type>\D+){1}(?P<num>\d+)?'
    match = re.match(type_re_pattern, wide_label)
    wide_type = match.group('type')
    match_num = match.group('num')
    
    converted_type = None
    for long_column, constructions in long_map.iteritems():
        if wide_type in constructions:
            converted_type = long_column
            return {'wide_label': wide_label,
                    'converted_type': converted_type,
                    'wide_type': wide_type,
                    'match_num': match_num,
                    }
    
    if converted_type is None:
        pass


def row_wtl(row, category='CHGS'):
    """Convert wide records to long

    row must be a dictionary with key/value pairs describing things like charges, diagnoses, or procedures.

    E.g.
        {
        'CHG1': 152.25,
        'RATE1': 790.0,
        'REVCD1': 128,
        ... ,
        'REVCD10': 278,
        }
    """
    longs = []
    key_labels = []
    

    if category in LONG_MAPS:
        long_map = LONG_MAPS[category]
    else:
        raise Exception("parse_wide_label() was called with category %s, but that category does not exist in LONG_MAPS (valid values are %s)" % (category, LONG_MAPS.keys()))    
    
    if category == 'CHGS':
        key_conv_type = 'CHARGE'
    else:
        key_conv_type = category
    
    for wide_label, value in row.iteritems():
        #one pass to get the charge labels
        parsed = parse_wide_label(wide_label, category)
        if parsed is not None and parsed['converted_type'] == key_conv_type:
            key_labels.append(parsed)
    
    for label in key_labels:
        match_num = label['match_num']
        charge_entry = {}
        
        for l, w_lst in long_map.iteritems():
            #l: long label
            #w_lst: list of corresponding wide labels
            unmatched = True
            
            for w_label in w_lst:
                if unmatched:
                    key = w_label + str(match_num)
                    if key in row:
                        unmatched = False
                        charge_entry[l] = row[key]
                        #print key, row
            
        longs.append(charge_entry)
    
    return longs


def df_wtl(wide_df, category='CHGS', row_id='KEY'):
    """Converts a DataFrame of wide-style procedure data into long-style procedure data

    Parameters
    =======================
    wide_df: pandas DataFrame object, required
        Contains wide data to be converted.

    category: string, required (default: 'CHGS')
        Category of wide data to be converted. Used to lookup LONG_MAPS definitions.

    row_id: string or list, required (default: 'KEY')
        Column name/label to use as identifier, which will be kept in the converted frame. Pass a list to preserve compound indexes.
    """
    
    # TODO: move this into LONG_MAPS somehow--these may need to be objects after all
    if category == 'CHGS':
        inclusion_lst = ['CHARGE']
    elif category == 'PR':
        inclusion_lst = ['PR', 'PRCCS']
    else:
        inclusion_lst = [category]
    
    long_dfs = []
    for i, row in wide_df.T.iteritems():
        # this is how to get the charges ready for input to row_wtl
        df = DataFrame(row_wtl(row.to_dict(), category))
        df[row_id] = row[row_id]
        long_dfs.append(df)
    
    c = pd.concat(long_dfs)
    #l = c[ (~c['PR'].isnull())|(~c['PRCCS'].isnull()) ].reset_index(drop=True).set_index(row_id)
    l = c[ (~c[inclusion_lst].apply(lambda x: x.isnull().any(), axis=1)) ].reset_index(drop=True).set_index(row_id)
    return l
