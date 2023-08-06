"""Read in and process data from HCUP (and Texas PUDF)
"""
import re
import pandas as pd
from pandas import DataFrame


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


def replace_df_sentinels(df, extra_dict=None):
    print "WARNING: This function has been renamed to replace_sentinels(). replace_df_sentinels() is scheduled for removal in version 0.1.6.0"
    return replace_sentinels(df, extra_dict)


def replace_sentinels(df, extra_dict=None):
    """Replaces HCUP SID sentinel patterns and values for bad data
    
    HCUP definitions from http://www.hcup-us.ahrq.gov/db/coding.pdf
    TX PUDF definitions from individual year manuals http://www.dshs.state.tx.us/thcic/hospitals/Inpatientpudf.shtm
    """
    import re, numpy
    
    patterns = {
        'missing':        '((?:-9*\.?9*)[^-\.]| |\.)',
        'invalid':        '((?:-8*\.?8*)[^-\.]|A)',
        'unavailable':    '((?:-7*\.?7*)[^-\.])',
        'inconsistent':   '((?:-6*\.?6*)[^-\.])',
        'notapplicable':  '((?:-5*\.?5*)[^-\.])',
        'tx_cell_too_sm': '(-?999+8)',
        'tx_invalid':     '(\*)',
        'tx_missing':     '(\.|`)',
        }
    if extra_dict is not None:
        patterns.update(extra_dict)
    
    sentinels_regex = re.compile('^%s$' % '|'.join(patterns.values()))
    df = df.applymap(lambda x: numpy.NaN if re.match(sentinels_regex, str(x)) is not None else x)
    return df


def replace_df_placeholders(df, extra_dict=None):
    dictionary = {'Y': 1, 'N': 0}
    if extra_dict is not None:
        dictionary.update(extra_dict)
        
    df = df.applymap(lambda x: dictionary.get(x) if x in dictionary else x)
    return df


# configuration of maps for converting wide to long
chgs_long_map = { #string_long_label: [list_of_wide_labels],
                 'CHARGE': ['CHG', 'REVCHG'],
                 'RATE': ['RATE'],
                 'REVCODE': ['REVCD'],
                 'UNITS': ['UNIT'],
                 }

dx_long_map = { #string_long_label: [list_of_wide_labels],
                'DX': ['DX'],
                'DXCCS': ['DXCCS'],
                'DXPOA': ['DXPOA'],
                'DXV': ['DXV'],
                'DXatAdmit': ['DXatAdmit'],
                }

pr_long_map = { #string_long_label: [list_of_wide_labels],
                'PR': ['PR'],
                'PRCCS': ['PRCCS'],
                'PRDATE': ['PRDATE'],
                'PRDAY': ['PRDAY'],
                'PRMCCS': ['PRMCCS'],
                'PRMONTH': ['PRMONTH'],
                'PRV': ['PRV'],
                'PRYEAR': ['PRYEAR'],
                'PCLASS': ['PCLASS'],
                }


def parse_wide_label(wide_label, long_map='CHGS'):
    """Breaks a wide format column label from a charges record into its component pieces.
    """
    
    if long_map == 'CHGS':
        long_map = chgs_long_map
    elif long_map == 'DX':
        long_map = dx_long_map
    elif long_map == 'PR':
        long_map = px_long_map
    
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


def row_wtl(row, row_type='CHGS'):
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
    
    
    if row_type == 'CHGS':
        long_map = chgs_long_map
        key_conv_type = 'CHARGE'
    elif row_type == 'DX':
        long_map = dx_long_map
        key_conv_type = 'DX'
    elif row_type == 'PR':
        long_map = pr_long_map
        key_conv_type = 'PR'
        
    
    for wide_label, value in row.iteritems():
        #one pass to get the charge labels
        parsed = parse_wide_label(wide_label, long_map)
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

# these three could doubtless be consolidated somehow
def chgs_df_wtl(wide_chgs_df):
    """Converts a DataFrame of wide-style charges data into long-style charges data
    """
    
    long_dfs = []
    for i, row in wide_chgs_df.T.iteritems():
        # this is how to get the charges ready for input to row_wtl
        df = DataFrame(row_wtl(row.to_dict(), row_type='CHGS'))
        df['KEY'] = i
        long_dfs.append(df)
    
    c = pd.concat(long_dfs)
    l = c[ ~c['CHARGE'].isnull() ].reset_index(drop=True)
    return l


def dx_df_wtl(wide_dx_df):
    """Converts a DataFrame of wide-style diagnosis data into long-style diagnosis data
    """
    long_dfs = []
    for i, row in wide_dx_df.T.iteritems():
        # this is how to get the charges ready for input to row_wtl
        df = DataFrame(row_wtl(row.to_dict(), row_type='DX'))
        df['KEY'] = i
        long_dfs.append(df)
    
    c = pd.concat(long_dfs)
    l = c[ ~c['DX'].isnull() ].reset_index(drop=True)
    return l


def pr_df_wtl(wide_dx_df):
    """Converts a DataFrame of wide-style procedure data into long-style procedure data
    """
    long_dfs = []
    for i, row in wide_dx_df.T.iteritems():
        # this is how to get the charges ready for input to row_wtl
        df = DataFrame(row_wtl(row.to_dict(), row_type='PR'))
        df['KEY'] = i
        long_dfs.append(df)
    
    c = pd.concat(long_dfs)
    l = c[ ~c['PR'].isnull() ].reset_index(drop=True)
    return l