"""Tools for getting HCUP data into a database.

Tested only with PostgreSQL 9.3 and not recommended for generating SQL statements.

In the long run, much of this would be better if it tied in something like SQLAlchemy.
"""
import pandas as pd
import datetime
import os

# move these into local namespace
import meta as pyhcup_meta
import parser
MISSING_PATTERNS = parser.MISSING_PATTERNS

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
    char_types = ['char', 'varchar', 'string', 's', 'alphanumeric', 'character']
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
        if scale < 1:
            #super sloppy
            if length > 9:
                data_type = 'BIGINT'
            else:
                data_type = 'INT'
        else:
            data_type = 'NUMERIC(%d, %d)' % (int(length), int(scale))
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
        allowed_constraints = ['NULL', 'NOT NULL', 'PRIMARY KEY', 'UNIQUE', 'DEFAULT NULL']
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


def table_sql(meta, table, schema=None, append_state=True,
                pk_fields=None, ine=False, default_constraints=None):
    """Generates SQL statement for creating a table based on columns in meta
    """
    if default_constraints == None:
        default_constraints = ['NULL']
        
    col_names = [x for x in meta.field.map(lambda x: x.lower()).values]
    column_clauses = [column_clause(x, default_constraints) for x in meta.T.to_dict().values()]
    
    if append_state:
        # append it only if it doesn't already exist
        if 'state' not in col_names:
            col_names.append('state')
            state_dict = {'field': 'state', 'length': 2, 'data_type': 'char'}
            state_clause = column_clause(state_dict)
            column_clauses.append(state_clause)
    
    if pk_fields is not None:
        for f in pk_fields:
            if f.lower() not in col_names:
                col_names.append(f.lower())
                # need to add this field to table columns, an int by default
                f_dict = {'field': f, 'length': 9, 'data_type': 'int'}
                f_clause = column_clause(f_dict)
                column_clauses.append(f_clause)
    
    sql = 'CREATE TABLE '
    if ine:
        sql += 'IF NOT EXISTS '
    
    if schema != None:
        #schema = 'public'
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


def create_table(cnxn, table_name, meta, schema=None, pk_fields=None,
                 ine=True, append_state=True, default_constraints=None,
                 index_pk_fields=True, indexes=None):
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
            index_stmt = index_sql(col, table_name, schema)
            cnxn.execute(index_stmt)
    
    cnxn.commit()
    
    return True


def long_table_sql(table_name, category, schema=None, ine=True, constraints=['DEFAULT NULL']):
    """Wraps table_sql(). Generates CREATE TABLE statement for a long table of the specified category.
    
    Also creates indexes on KEY, VISITLINK, YEAR, and STATE.
    
    Parameters
    ===============
    table_name: string, required
        Name to be used for creating the table
        
    category: string, required
        Category of long table to be created. Valid options for HCUP are 'CHGS', 'DX', 'PR'.
    """
    
    if not isinstance(category, (str, unicode)):
        raise Exception("category must be a str or unicode (got %s)" % type(category))
    
    # these are the base fields to start with for any long table
    # though, PUDF will typically not have visitlink records, I don't think.
    # So, those will have to be added back in in a separate step :(
    fields = [
        dict(field='KEY', length=18, data_type='numeric'),
        dict(field='VISITLINK', length=18, data_type='numeric'),
        dict(field='YEAR', length=5, data_type='numeric'),
        dict(field='STATE', length=2, data_type='char'),
    ]
    
    if category == 'CHGS':
        fields += [
            dict(field='UNITS', length=11, data_type='numeric', scale=2),
            dict(field='REVCODE', length=4, data_type='char'),
            dict(field='RATE', length=9, data_type='numeric', scale=2),
            dict(field='CHARGE', length=12, data_type='numeric', scale=2),
        ]
    elif category == 'DX':
        fields += [
            dict(field='DX', length=10, data_type='char'),
            dict(field='DXV', length=2, data_type='char'),
            dict(field='DXCCS', length=5, data_type='char'),
            dict(field='DXPOA', length=1, data_type='char'),
            dict(field='DXatAdmit', length=1, data_type='char'),
            dict(field='TMDX', length=1, data_type='char'),
        ]
    elif category == 'PR':
        fields += [
            dict(field='PR', length=10, data_type='char'),
            dict(field='PRCCS', length=5, data_type='char'),
            dict(field='PRDATE', length=6, data_type='char'),
            dict(field='PRDAY', length=2, data_type='char'),
            dict(field='PRMONTH', length=2, data_type='char'),
            dict(field='PRYEAR', length=4, data_type='char'),
            dict(field='PRV', length=2, data_type='char'),
            dict(field='PCLASS', length=1, data_type='char'),
            dict(field='PRMCCS', length=8, data_type='char'),
        ]
    else:
        raise Exception("At present only long charges (CHGS), diagnosis (DX), and procedure (PR) category tables are supported. (Got %s)" % category)

    fields_df = pd.DataFrame(fields)
    
    # correct for NaN scale values so column_clause doesn't flip out
    fields_df.scale = fields_df.scale.map(lambda x: False if pd.isnull(x) else x)
    
    sql = table_sql(fields_df, table_name, schema=schema, ine=True)
    
    return sql


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
        row = v[1:] # first item in the values tuple is the index, which we do not want to insert
        param_subset = ', '.join(placeholder for x in row)
        param_strings.append('(%s)' % param_subset)
        values.extend([cast_to_py(y) for y in row])

    param_placeholders = ', '.join(param_strings)
    insert_sql = 'INSERT INTO '
    if schema is not None:
        insert_sql += '%s.' % str(schema)
    insert_sql += '%s (%s) VALUES %s' % (table, ', '.join(df.columns.values), param_placeholders)
    
    return insert_sql, values


def pg_rawload(cnxn, handle, meta_df, dummy_separator="|"):
    """Uses psycopg2 methods to load raw data into a one-column table.

    Uses default schema; no support for specifying schema inside this function.

    Returns the name of the created table. Any check of the COPY'd count versus the handle length will have to take place elsewhere.

    Parameters
    ==========
    cnxn: required
        Must be a connection created by psycopg2.connect().
    
    handle: required
        Must be a file-like object. I.e., returned by open(path).

    meta_df: required
        Must be a pandas DataFrame with meta data on the file in question. I.e., returned by pyhcup.meta.get().

    dummy_separator: required (default: "|")
        Must be a character not found in the data to be loaded. The psycopg2.cursor.copy_from() method uses a tab ('\t') by default, which may result in inconsistent loads if found within the data to be loaded. The default pipe character is considered a safe choice, though it has not been exhaustively tested against all HCUP data.

    """
    
    try:
        import psycopg2
    except ImportError:
        raise ImportError("The pg_rawload() function requires psycopg2 to be installed.")
    
    # get the filename sans extension for use in making a table name
    base_filename = os.path.split(handle.name)[-1].split('.')[0]
    
    # make a timestamp in YYYYMMDDhhmmss format
    # will be used as part of the table name
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y%m%d%H%M%S')
    
    raw_table_name = '%s%s_raw' % (base_filename, timestamp)
    
    
    # acquire a cursor from the connection object
    cursor = cnxn.cursor()
    
    
    # proceed to table creation
    # WARNING: this is a SQL injection vector, where a clever filename can
    # execute arbitrary SQL commands
    raw_table_create_sql = 'CREATE TABLE IF NOT EXISTS %s (line TEXT);' % raw_table_name
    cursor.execute(raw_table_create_sql)
    cnxn.commit()
    
    
    # load the data using psycopg2.cursor.copy_from() method
    cursor.copy_from(handle, raw_table_name, sep=dummy_separator)
    cnxn.commit()
    
    return raw_table_name


def pg_staging(cnxn, raw_table_name, meta_df, state, year,
               pk_fields=['key', 'state', 'year'],
               replace_sentinels=True):
    """Uses PostgreSQL functions to split raw load table into columns, scrub missing data placeholders, load the results into a new table.

    Uses default schema; no support for specifying schema inside this function.

    Returns a tuple containing the name of the created table and the number of affected rows.

    Parameters
    ==========
    cnxn: required
        Must be a connection created by psycopg2.connect().
    
    raw_table_name: required
        Must be a string; should be the name of a table created with pg_rawload().

    meta_df: required
        Must be a pandas DataFrame with meta data on the file in question. I.e., returned by pyhcup.meta.get().

    state: required
        Should be the two letter abbreviation for the state where the data are from, like 'NE' for Nebraska. Used to fill in the state value explicitly in the table.

    year: required
        Should be the four digit year where the data are from, like 2009. Used to fill in the year value explicitly in the table.
    
    pk_fields: required (list or None)
        Will create a primary key and indexes using these fields. A list with length greater than 1 results in a compound primary key.
    """
    
    try:
        import psycopg2
    except ImportError:
        raise ImportError("The pg_staging() function requires psycopg2 to be installed.")
    
    # derive a name for this staging table
    # prefer to have it match the raw table name, but with staging instead of raw
    # failing that, just tack on '_staging' to the other name
    if 'raw' in raw_table_name:
        staging_table_name = raw_table_name.replace('raw', 'staging')
    else:
        staging_table_name = raw_table_name + '_staging'
    
    # acquire a cursor from the connection object
    cursor = cnxn.cursor()
    
    # augment this meta_df so we have access to more information regarding column contents
    # and can therefore derive explicit PostgreSQL column cast declarations.
    # this is valuable since the table will be created using the same column casting in
    # result of the SELECT statement.
    meta_df = pyhcup_meta.augment(meta_df)
    
    # borrow the MISSING_PATTERNS definition in pyhcup to use for missing data
    # replacement (substitutes NULL whenever a match is found down the line)
    missing_pattern = '|'.join(['^%s$' % val for k, val in MISSING_PATTERNS.iteritems()])
    
    # construct clauses for deriving each of the columns
    # WARNING: This is another potential site of SQL injection, as these values
    # are not passed as bind parameters.
    
    substr_clauses = ['''
        NULLIF(TRIM(REGEXP_REPLACE(SUBSTRING(line FROM %s FOR %s), '%s', '')), '')::%s AS %s
        ''' % (row['position'], row['width'], missing_pattern, pg_castcoltype(row['data_type'], row['length'], row['scale']), row['field'])
        for i, row in meta_df.T.iterkv()
        if row['field'].lower() not in ['state', 'year']
    ]
    
    # add those year and state values as scalars
    col_clauses = substr_clauses + ['%s::INT AS YEAR' % year, "'%s'::VARCHAR AS STATE" % state]
    
    
    # first create the table
    
    
    # then do an INSERT INTO... SELECT... style statement to move it over
    
    # proceed to table creation
    staging_table_create_sql = '''
        CREATE TABLE %s AS
            SELECT %s
            FROM %s
        ;
        ''' % (staging_table_name, ', '.join(col_clauses), raw_table_name)
    cursor.execute(staging_table_create_sql)
    cnxn.commit()
    affected_rows = cursor.rowcount
    
    # Really, the steps below may be unnecessary.
    # If this table will soon be selected into a master table with
    # constraints already in place, then this is a redundant (and
    # slow!) step to perform twice.
    # It is good to put in for now for validating that this approach
    # is not truncating fields, and as a comparison of overall
    # loading speed.
    
    if pk_fields is not None:
        if isinstance(pk_fields, list) and len(pk_fields) > 0:
            for col in pk_fields:
                index_stmt = index_sql(col, staging_table_name)
                cursor.execute(index_stmt)
                cnxn.commit()
    
            pk_sql = """
                ALTER TABLE %s ADD PRIMARY KEY(%s);
                """ % (staging_table_name, ', '.join(pk_fields))
            cursor.execute(pk_sql)
            cnxn.commit()
        
        else:
            raise TypeError("pk_fields must either be None or a non-zero length list (got %s)." % type(pk_fields))
    
    return staging_table_name, affected_rows


def pg_castcoltype(archtype, length, scale=None, all_char_as_varchar=True):
    """Generates an explicit column casting from an archtype, length, and optional scale value.

    These are typically values dictionaries from a meta_df object, accessed as meta_df.to_dict().values().
    """
    
    char_types = ['char', 'varchar', 'string', 's', 'alphanumeric', 'character']
    num_types = ['numeric', 'number', 'float', 'decimal', 'dec', 'd', 'f', 'numeric']
    int_types = ['int', 'integer', 'i']
    boolean_types = ['boolean', 'truefalse', 'tf', 'truth']
    
    length = int(length)
    
    if archtype.lower() in char_types:
        if all_char_as_varchar:
            data_type = 'VARCHAR'
        else:
            data_type = 'VARCHAR(%s)' % length
    elif archtype.lower() in num_types:
        if not scale:
            scale = 0
        
        if scale < 1:
            #super sloppy
            if length > 9:
                data_type = 'BIGINT'
            else:
                data_type = 'INT'
        else:
            data_type = 'NUMERIC(%d, %d)' % (int(length), int(scale))
    elif archtype.lower() in int_types:
        if length > 9:
            data_type = 'BIGINT'
        else:
            data_type = 'INT'
    elif archtype.lower() in boolean_types:
        data_type = 'BOOLEAN'
    else:
        raise Exception("Unable to cast column data type from data_type \"%s\"" % archtype)
    
    return data_type


def pg_wtl_shovel(cnxn, meta_df, category, tbl_source,
        tbl_destination, extra_fields=['state', 'year', 'key']):
    """Shovels wide things into long things
    
    category is 'CHGS' only, for now
    """
    lm = parser.LONG_MAPS[category]

    reverse_lm = {}
    field_s = meta_df.field

    for des_col, in_col_lst in lm.iteritems():
        matched = False
        for in_candidate in in_col_lst:
            # Look at the candidates for incoming field
            # and see if there is a match for the candidate
            # among the incoming meta columns, minus one char.
            # This is to accommodate things like CHG1, so that
            # it matches CHG.
            if (
                not matched and
                in_candidate in field_s.map(lambda x: str(x)[:-1]).values
                ):
                reverse_lm[in_candidate] = des_col
                matched = True

    assert all([isinstance(v, str) for k, v in reverse_lm.iteritems()]), \
        "Somehow the match in the reverse long map is not a string."

    # We tolerate missing cols (e.g., no RATE provided), but not extra cols.
    assert len(reverse_lm) <= len(lm), \
        "Ended up with more reverse long map entries than long map entries."


    # Get the max number of each variety of column
    maxes = []
    for k in reverse_lm.keys():
        fields_containing = field_s[ field_s.map(lambda x: k in x) ]
        nums = fields_containing.map(lambda x: x.split(k)[1])
        maxes.append(nums.astype(int).max())

    # Make sure we have the same number of each variety of column
    assert all([x == maxes[0] for x in maxes]), \
        "One or more columns to be longed has an unusual number of columns. Please inspect the data."
    groups = maxes[0]

    # Select groups of these columns, up to n, to use for input
    shoveled = 0

    for x in xrange(1, groups+1):
        cols_select = ['%s%s' % (k, x) for k in reverse_lm.keys()]
        cols_as = reverse_lm.values()
        
        if isinstance(extra_fields, list) and len(extra_fields) > 0:
            # some extra fields are requested; likely state, year, and key
            cols_select += extra_fields
            cols_as += extra_fields
        
        # only drop tables after doing the final shovel
        if x == groups:
            preserve_source = True
        else:
            preserve_source = False
        
        if category == 'CHGS':
            wnn = ['CHG%s' % x]
        else:
            wnn = None
        
        shoveled += pg_shovel(cnxn, tbl_source, tbl_destination, cols_select,
            cols_as, where_not_null=wnn, preserve_source=preserve_source)
    
    return shoveled


def pg_shovel(cnxn, tbl_source, tbl_destination, fields_in, fields_out=False,
              where_not_null=None, preserve_source=False):
    """Attempts to move everything in tbl_source to tbl_destination using cnxn.
    
    The SQL used here is supported for sure in PostgreSQL but untested in other engines.

    fields_out must either be False or a list with length len(fields_in). These will be used as "SELECT {field_in} AS {field_out}" to map values to differently named columns.
    
    If preserve_source is False, the table will be dropped after the transfer.
    """
    cursor = cnxn.cursor()
    
    if fields_out:
        assert len(fields_out) == len(fields_in), \
            "If provided, fields_out must have the same length as fields_in."
        select_fields = ', '.join(['%s AS %s' % cols for cols in zip(fields_in, fields_out)])
        insert_fields = ', '.join(fields_out)
    else:
        select_fields = ', '.join(fields_in)
        insert_fields = ', '.join(fields_in)
    
    stmt = '''
        INSERT INTO %s (%s)
            SELECT %s FROM %s
        ''' % (str(tbl_destination), insert_fields, select_fields, str(tbl_source))
    
    if where_not_null is not None:
        assert isinstance(where_not_null, list), \
            "If provided, where_not_null must be a list (got %s)." % (type(where_not_null))
        
        assert all([x in fields_in for x in where_not_null]), \
            "If provided, all items in where_not_null must be items in fields_in (got %s and %s, respectively)." % (where_not_null, field_in)
        
        stmt += 'WHERE (%s)' % (' AND '.join(['%s IS NOT NULL' % wnn for wnn in where_not_null]))
    
    
    cursor.execute(stmt)
    cnxn.commit()
    
    if cursor.rowcount > 0:
        return cursor.rowcount
    else:
        return False


def pg_drop(cnxn, tbl_name):
    cursor = cnxn.cursor()
    stmt = 'DROP TABLE IF EXISTS %s;' % tbl_name
    cursor.execute(stmt)
    cnxn.commit()
    
    if cursor.statusmessage == 'DROP TABLE':
        return True
    else:
        return cursor.statusmessage
