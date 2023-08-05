"""Tools for processing HCUP SID meta and data frames.

Provides additional functionality specific to HCUP SID files beyond the SAS parsing provided by the sas_import module."""
import re
import numpy as np

def replace_df_sentinels(df, extra_dict=None):
    """Replaces HCUP SID sentinel patterns and values for bad data
    
    Definitions from http://www.hcup-us.ahrq.gov/db/coding.pdf
    """
    patterns = {
        'missing':        '((?:-9*\.?9*)[^-\.]| |\.)',
        'invalid':        '((?:-8*\.?8*)[^-\.]|A)',
        'unavailable':    '((?:-7*\.?7*)[^-\.])',
        'inconsistent':   '((?:-6*\.?6*)[^-\.])',
        'notapplicable':  '((?:-5*\.?5*)[^-\.])',
        }
    if extra_dict is not None:
        patterns.update(extra_dict)
    
    sentinels_regex = re.compile('^%s$' % '|'.join(patterns.values()))
    df = df.applymap(lambda x: np.NaN if re.match(sentinels_regex, str(x)) is not None else x)
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