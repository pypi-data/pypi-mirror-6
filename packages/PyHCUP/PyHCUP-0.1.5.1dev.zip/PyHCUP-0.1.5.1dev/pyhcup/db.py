"""Tools for getting HCUP data into a database.

Mostly focused on casting column data types and lengths from meta data in SAS loading programs.

"""

def column_clause(dictionary, constraints=None):
    """Builds a SQL column definition from information in a dictionary record
    
    """
    char_types = ['char', 'varchar', 'string', 's']
    num_types = ['numeric', 'number', 'float', 'decimal', 'dec', 'd', 'f']
    int_types = ['int', 'integer', 'i']
    
    name = dictionary['field']
    length = int(dictionary['length'])
    
    if dictionary['data_type'] in char_types:
        data_type = 'VARCHAR(%s)' % length
    elif dictionary['data_type'] in num_types:
        data_type = 'NUMERIC(%s, %s)' % (length, dictionary['scale'])
    elif dictionary['data_type'] in int_types:
        if length > 9:
            data_type = 'BIGINT'
        else:
            data_type = 'INT'
    else:
        raise Exception("Unable to cast column data type from data_type \"%s\"" % dictionary['data_type'])
    
    clause = '%s %s' % (name, data_type)
    if constraints is not None:
        allowed_constraints = ['NULL', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE']
        constrained_by = [x for x in constraints if x.upper() in allowed_constraints]
        if len(constrained_by) > 0:
            clause = '%s %s' % (clause, ' '.join(constrained_by))
    
    return clause

def col_from_invalue(invalue):
    """Takes an HCUP SID invalue name and infers details on appropriate database column type.

    With a single exception the INFORMAT definitions in the *CORE.sas files are actual invalue vars declared earlier. Fortunately those invalue variables appear to use a standardized naming convention that infers the type and formatting of the data in that column.

    The exception is KEY fields, which use a true SAS INFORMAT definition but which are all integers anyways.

    Returns a dictionary with column type details.
    """
    result = {'invalue': invalue}
    result['scale'] = False #default
    key_regex = re.compile('(?P<length>\d+).')
    numeric_regex = re.compile('(N(?P<full_length>\d+)P(?P<scale>\d*)F)')
    char_regex = re.compile('\$CHAR(?P<length>\d+)')
    
    key_capture = re.search(key_regex, invalue)
    numeric_capture = re.search(numeric_regex, invalue)
    char_capture = re.search(char_regex, invalue)

    if char_capture is not None:
        groups = char_capture.groupdict()
        result['type'] = 'char'
        result['length'] = int(groups['length'])
        
    elif numeric_capture is not None:
        groups = numeric_capture.groupdict()
        
        #at this point some adjustments have to be made
        #the full_length value includes a position for sign and a decimal, if needed
        result['length'] = int(groups['full_length'])# - 1  #unpad from sign #commented out because it is shorting the length
        if groups['scale'] == '':
            result['scale'] = 0
        else:
            result['scale'] = int(groups['scale'])
        
        if result['scale'] > 0:
            result['type'] = 'numeric'
        else:
            result['type'] = 'int'
    elif key_capture is not None:
        result['length'] = int(key_capture.groupdict()['length'])
        result['type'] = 'int'#TODO: add support for bigint for key and any other lengthy ints
    
    else:
        raise Exception('Unable to to determine column type details. %s is not numeric, character, or key field.' % (invalue))
    
    return result