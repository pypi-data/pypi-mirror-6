PyHCUP is a Python library for parsing and importing data obtained from the Healthcare Cost and Utilization Program (http://hcup-us.ahrq.gov).

In particular, most of the data provided by HCUP is in fixed-width text (ASCII or \*.asc) files, with meta data available in separate load files. This library is built to use the SAS format load files (\*.sas).

Example Usage
================================================

Load a datafile/loadfile combination.::

    import pyhcup
 
    #specify where your data and loadfiles live
    datafile = 'D:\\Users\\hcup\\sid\\NY_SID_2009_CORE.asc'
    loadfile = 'D:\\Users\\hcup\\sid\\sasload\\NY_SID_2009_CORE.sas'
 
    #pull basic meta from SAS loadfile
    meta_df = pyhcup.sas.meta_from_sas(loadfile)
    
    #use meta knowledge to parse datafile into a pandas DataFrame
    df = pyhcup.sas.df_from_sas(datafile, meta_df)

Deal with very large files that cannot be held in memory in two ways.

1) To import a subset of rows, such as for preliminary work or troubleshooting, specify nrows to read and/or skiprows to skip using sas.df_from_sas()::

    #optionally specify nrows and/or skiprows to handle larger files
    df = pyhcup.sas.df_from_sas(datafile, meta_df, nrows=5*10**5, skiprows=10**6)

2) To iterate through chunks of rows, such as for importing into a database, first use the metadata to build lists of column names and widths. Next, pass a chunksize to the df_from_sas() function above to create a generator yielding manageable-sized chunks.::

    chunk_size = 500000
    reader = pyhcup.sas.df_from_sas(datafile, meta_df, chunksize=chunk_size)
    for df in reader:
        #do your business
        #such as replacing sentinel values (below)
        #or inserting into a database with another Python library

Whether you are pulling in all records or just a chunk of records, you can also replace all those pesky missing/invalid data placeholders from HCUP (this is less useful for generically parsing missing values for non-HCUP files).::

    #also, this bulldozes through all values in all columns with no per-column control
    replaced = pyhcup.parser.replace_df_sentinels(df)