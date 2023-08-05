"""Tools for getting HCUP data into a database.

Tested only with PostgreSQL 9.3 and not recommended for generating SQL statements.

In the long run, much of this would be better if it tied in something like SQLAlchemy.
"""

def column_clause(dictionary, constraints=None, all_char_as_varchar=True):
    """Builds a SQL column definition from information in a dictionary record
    
    Long-term, this should probably be replaced with functionality from a more mature library like SQLAlchemy.
    
    Expected keys:
        data_type -> string, column type such as char, numeric, int, or boolean
        field -> string, name for column
        length -> int, width of maximum column value for char and int types; precision for numeric types
    
    Optional keys:
        scale -> int, number of decimal places (e.g. 2 for values like 3.14)
    """
    char_types = ['char', 'varchar', 'string', 's', 'alphanumeric']
    num_types = ['numeric', 'number', 'float', 'decimal', 'dec', 'd', 'f', 'numeric']
    int_types = ['int', 'integer', 'i']
    boolean_types = ['boolean', 'truefalse', 'tf', 'truth']
    
    name = dictionary['field']
    length = int(dictionary['length'])
    
    if dictionary['data_type'].lower() in char_types:
        if all_char_as_varchar:
            data_type = 'VARCHAR'
        else:
            data_type = 'VARCHAR(%s)' % length
    elif dictionary['data_type'].lower() in num_types:
        if 'scale' in dictionary:
            scale = dictionary['scale']
        else:
            scale = 0
        if scale == 0:
            #super sloppy
            if length > 9:
                data_type = 'BIGINT'
            else:
                data_type = 'INT'
        else:
            data_type = 'NUMERIC(%d, %d)' % (length, scale)
    elif dictionary['data_type'].lower() in int_types:
        if length > 9:
            data_type = 'BIGINT'
        else:
            data_type = 'INT'
    elif dictionary['data_type'].lower() in boolean_types:
        data_type = 'BOOLEAN'
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
    import re
    
    #TODO: Move this to sas module?
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

def table_sql(meta, table, schema=None, append_state=True, pk_fields=None, ine=False, default_constraints=None):
    """Generates SQL statement for creating a table based on columns in meta
    """
    if default_constraints == None:
        default_constraints = ['NULL']
    column_clauses = [column_clause(x, default_constraints) for x in meta.T.to_dict().values()]
    if append_state:
        state_dict = {'field': 'state', 'length': 2, 'data_type': 'char'}
        state_clause = column_clause(state_dict)
        column_clauses.append(state_clause)
    
    schema = 'public'
    sql = 'CREATE TABLE '
    if ine:
        sql += 'IF NOT EXISTS '
    if schema != None:
        sql += '%s.' % schema
    sql += '%s' % table
    sql += '(%s' % ', '.join(column_clauses)
    if type(pk_fields) == list:
        sql += ', PRIMARY KEY(%s)' % ', '.join(pk_fields)
    sql += ');'
    
    return sql

def index_sql(field, table, schema=None):
    """Generates SQL statement for creating an index
    """
    sql = 'CREATE INDEX ON '
    if schema != None:
        sql += '%s.' % schema
    sql += '%s (%s);' % (table, field)
    return sql

def create_table(cnxn, table_name, meta, schema=None, pk_fields=None, ine=True, append_state=True, default_constraints=None, index_pk_fields=True, indexes=None):
    """Wrapper to generate and execute SQL statements for table and index creation
    
    pk_fields should be a list of fields to use as a composite primary key on the new table
    """
    create = table_sql(meta, table_name, schema, pk_fields=pk_fields, ine=ine, append_state=append_state, default_constraints=default_constraints)
    cnxn.execute(create)
    
    if index_pk_fields:
        if type(indexes) == list:
            indexes.extend(pk_fields)
        else:
            indexes = pk_fields
    
    if indexes != None:
        for col in pk_fields:
            index = index_sql(col, table_name, schema)
            cnxn.execute(index)
    
    cnxn.commit()
    pass

def cast_to_py(x):
    """Casts type to native Python types, mainly so they can be passed on as bind params for SQL"""
    import numpy as np
    import math
    
    int_types = [int, np.int, np.int64, np.int32, np.int16]
    float_types = [float, np.float, np.float64, np.float16, np.float32]
    str_types = [str]
    if type(x) in float_types:
        if math.isnan(x) or np.isnan(x):
            return None
        else:
            return float(x)
    elif type(x) in int_types:
        return int(x)
    elif type(x) in str_types:
        return str(x)
    else:
        return x

def insert_sql(df, table, schema=None, placeholder="%s"):
    """Returns a tuple (parameterized SQL, list of params) for an insert statement
    
    df: required
        DataFrame to build the insert off of. df.columns will be used as column names in the insert statement.
    
    table: required
        Name of table to build the insert into.
    
    schema: optional
        Namespace for the table. If provided, will be prepended with dot notation as schema.table.
    
    placeholder: optional
        String to use as placeholder in creating parameterized expression. Default is "%s" but "?" is also common.
    """
    param_strings = []
    values = []
    
    for v in df.reset_index(drop=True).itertuples():
        row = v[1:]
        param_subset = ', '.join(placeholder for x in row)
        param_strings.append('(%s)' % param_subset)
        values.extend([cast_to_py(y) for y in row])

    param_placeholders = ', '.join(param_strings)
    insert_sql = 'INSERT INTO '
    if schema is not None:
        insert_sql += '%s.' % str(schema)
    insert_sql += '%s (%s) VALUES %s' % (table, ', '.join(df.columns.values), param_placeholders)
    
    return insert_sql, values