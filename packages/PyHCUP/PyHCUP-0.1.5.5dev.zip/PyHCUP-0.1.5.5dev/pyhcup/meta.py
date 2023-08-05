"""Functions for getting and working with meta data

"High-level" module which imports other pyhcup modules as part of its work
"""

#these should never import this module or a circular dependecy will result
from pyhcup import hachoir, sas, tx

def get(state, year, variety):
    """Builds requested meta DataFrame using packaged data
    
    Note that this is not terribly efficient as it relies on crawling the loadfile directory each time it is called.
    """
    
    result_meta_df = None
    
    #by default, hachoir.discover() is pointed at the bundled loadfiles
    available_loadfiles = hachoir.discover()
    
    #for all requested states _except_ for Texas or TX, look for an HCUP file
    if state.lower() in ['texas', 'tx']:
        source = 'pudf'
    else:
        source = 'hcup'

    match = None    
    for lf in available_loadfiles:
        if match is None:
            if (
                lf['source'].lower() == source and
                lf['state_abbr'].lower() == state.lower() and
                lf['variety'].lower() == variety.lower() and
                lf['year'] == str(year)#cuz the regex will have found year as a string
                ):
                match = lf['full_path']
                if source == 'pudf':
                    #use tx functions to make the meta DataFrame
                    result_meta_df = tx.meta_from_txt(match)
                else:
                    result_meta_df = sas.meta_from_sas(match)

    return result_meta_df
    