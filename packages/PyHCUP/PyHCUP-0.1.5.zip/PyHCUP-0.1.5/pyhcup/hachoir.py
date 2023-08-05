"""Tools for traversing disk, discovering files, matching load program files to content (*.asc) files, and batching imports.

Intended to work primarily with an accompanying Django app, but functionality may be back-ported into here.
"""
import re, os, zipfile

def discover(root_path, sources=None):
    """Looks for files in root_path (and below) that match various patterns supplied in sources. Returns a list of hits or None if no hits found.

    sources should be a list containing dictionaries that specify str data_source, str description, and dict patterns. Each value in patterns must be a regular expression representing a file naming convention.
    
    Here is an example of a source dictionary.
        
        {
        'data_source': 'SID',
        'description': 'Healthcare Cost and Utilization Project State Inpatient Database',
        'patterns': {
            'content': '(?P<state_abbr>[A-Z]{2})_(SID|SIDC)_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>asc)',
            'content_zipped': '(?P<state_abbr>[A-Z]{2})_(SID|SIDC)_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>(exe|zip))',
            'load': '(?P<state_abbr>[A-Z]{2})_(SID|SIDC)_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>sas)',
            },
        }
    
    Each discovered hit will contain, at a minimum, filename, full_path, directory, match_type, source, and size_on_disk. Hits will also contain any other named captured values specified in the regular expression pattern that found them.
    
    """
    if sources is None:
        #use default sources
        sources = [
            {
            'data_source': 'SID',
            'description': 'Healthcare Cost and Utilization Project State Inpatient Database',
            'patterns': {
                'content': '(?P<state_abbr>[A-Z]{2})_(SID|SIDC)_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>asc)',
                'content_zipped': '(?P<state_abbr>[A-Z]{2})_(SID|SIDC)_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>(exe|zip))',
                'load': '(?P<state_abbr>[A-Z]{2})_(SID|SIDC)_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>sas)',
                },
            },
            {
            'data_source': 'SEDD',
            'description': 'Healthcare Cost and Utilization Project State Emergency Department Database',
            'patterns': {
                'content': '(?P<state_abbr>[A-Z]{2})_SEDD_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>asc)',
                'content_zipped': '(?P<state_abbr>[A-Z]{2})_SEDD_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>exe|zip)',
                'load': '(?P<state_abbr>[A-Z]{2})_SEDD_(?P<year>[0-9]{4})_(?P<file_type>[A-Z]+)\.(?P<file_extension>sas)',
                }
            },
            ]
    
    hits = []
    for directory, dirs, files in os.walk(root_path):
        #http://docs.python.org/2/library/os.html#os.walk
        
        #loop through files each time some are found
        for filename in files:
            
            #check file against possible sources by examining filename for known patterns
            for source in sources:
                for match_type, pattern in source['patterns'].iteritems():
                    match = re.match(pattern, filename)
                    if match is not None:
                        full_path = directory+'\\'+filename
                        hit = {
                            'filename': filename,
                            'full_path': full_path,
                            'directory': directory,
                            'match_type': match_type,
                            'source': source['data_source'],
                            'size_on_disk': os.stat(full_path).st_size
                            }
                        hit.update(match.groupdict())
                        hits.append(hit)
    
    if len(hits) > 0:
        return hits
    else:
        return None

def openz(path, filename, target=None):
    """Open a zipped archive and return a file-like object from it.
    
    path should have appropriately escaped solidus at the end of it, ie '/' for Linux and '\\' for Windows
    
    If target is None, look for a file in archive matching the passed filename sans file_extension. If no such match, check to see if only one file and use that.
    """
    with zipfile.ZipFile(path+filename) as z:
        if target is None:
            matched = False
            for zname in z.namelist():
                if not matched:
                    no_ext_zname = zname.split('.')[-1]
                    no_ext_filename = filename.split('.')[-1]
                    if no_ext_zname == no_ext_filename:
                        #found the match
                        target = zname
                        matched = True
                        print "matched"
            
            if not matched:
                #still not matched
                #last chance is to check to see if the length of the filenames is one, and just use that one
                if len(z.namelist()) == 1:
                    target = z.namelist()[0]
                else:
                    raise Exception("Unable to determine target file in archive %s" % path+filename)
        
        handle = z.open(target)
        return handle