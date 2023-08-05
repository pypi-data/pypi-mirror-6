"""Read in and process data from HCUP (and Texas PUDF)
"""

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

def augment_meta_df(meta_df):
    """Uses informat data pulled from SAS loadfile to derive additional information about columns
    
    Returns: processed meta dataframe.
    """
    
    #avoid a circular reference
    from pyhcup.db import col_from_invalue

    meta_df['length'] = meta_df['informat'].map(lambda x: col_from_invalue(x)['length'])
    meta_df['data_type'] = meta_df['informat'].map(lambda x: col_from_invalue(x)['type'])
    meta_df['scale'] = meta_df['informat'].map(lambda x: col_from_invalue(x)['scale'])
    meta_df['numeric_or_int'] = meta_df['data_type'].map(lambda x: True if x in ['int', 'numeric'] else False)
    return meta_df

def chgs_wtl(row, sid_key=None):
    """Convert wide charges records to long

    row must be a dictionary with key/value pairs describing charges.

    E.g.
        {
        'CHG1': 152.25,
        'RATE1': 790.0,
        'REVCD1': 128,
        ... ,
        'REVCD10': 278,
        }
    """
    charges = []
    charge_labels = []
    
    for wide_label, value in row.iteritems():
        #one pass to get the charge labels
        parsed = parse_wide_chgs_label(wide_label)
        if parsed['converted_type'] == 'CHARGE':
            charge_labels.append(parsed)
    
    for charge_label in charge_labels:
        match_num = charge_label['match_num']
        amount = None
        rate = None
        revcode = None
        units = None
        
        charge_key = 'CHG' + match_num
        
        if charge_key in row:
            amount = row[charge_key]
        
        if amount > 0:
            #recast this to prevent weird float errors
            amount = str(amount)
            
            rate_key = 'RATE' + match_num
            if rate_key in row:
                rate = row[rate_key]
            
            revcode_key = 'REVCD' + match_num
            if revcode_key in row:
                revcode = row[revcode_key]
            
            units_key = 'UNIT' + match_num
            if units_key in row:
                units = row[units_key]
            
            charge_entry = {'KEY': sid_key,
                      'CHARGE': amount,
                      'RATE': rate,
                      'REVCODE': revcode,
                      'UNITS': units,
                      }
            charges.append(charge_entry)
    
    return charges

def parse_wide_chgs_label(wide_label, type_re_pattern='(?P<type>\D+){1}(?P<num>\d+)?'):
    """Breaks a wide format column label from a charges record into its component pieces"""
    import re
    
    long_map = {#string_long_label: [list_of_wide_labels],
                'CHARGE': ['CHG'],
                'RATE': ['RATE'],
                'REVCODE': ['REVCD'],
                'UNITS': ['UNIT'],
                }
    
    match = re.match(type_re_pattern, wide_label)
    wide_type = match.group('type')
    match_num = match.group('num')
    
    #use long_map to see what long_column the wide_type corresponds to
    #for example wide label 'CHG' matches up with long column 'CHARGE'
    #throw an exception if unable to find a suitable match
    converted_type = None
    for long_column, constructions in long_map.iteritems():
        if wide_type in constructions:
            converted_type = long_column
    
    if converted_type is None:
        raise Exception("Unable to find suitable long_column for wide_type %s" % wide_type)
    
    return {'wide_label': wide_label,
            'converted_type': converted_type,
            'wide_type': wide_type,
            'match_num': match_num,
            }