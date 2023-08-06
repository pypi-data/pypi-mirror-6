from datetime import datetime
import numpy as np

from obspy.core import UTCDateTime
from pisces.schema.util import get_infovals


# TODO: replace numpy.genfromtxt with pandas.read_fwf ?

def format_records(recs, meta, structure):
    """
    Get a well-formatted rec.array of records with requested structure.

    Returned array has the desired field order with any missing values.

    recs: numpy structured array
    meta: sqlalchemy.MetaData 
        Columns in tables must have info['dtype'] and info['width']
    structure: iterable of str
        The structure of the text file.  Strings are known schema objects 
        (tables, columns).  Duplicate column names will be overwritten!


    """
    # The Plan:
    # 1) Make 2 new intermediate record arrays.  1 contains missing values for
    #    all expected columns not in the incoming array, the other is empty and
    #    has the requested output structure.
    # 2) Fill in the empty recarray with either values from the incoming array,
    #    or, if not present, pull from the missing value array. Return it.

    # get flat expected field names and defaults from structure
    fields, dflts = get_infovals(meta, structure, 'default')
    mdict = dict(zip(fields, dflts))

    # initialize output array
    fields, dtypes = get_infovals(meta, structure, 'dtype')
    dtp = np.dtype(zip(fields, dtypes))
    newrecs = np.recarray(recs.shape, dtype=dtp)

    # fill in any missing values
    for field in fields:
        try:
            newrecs[field] = recs[field]
        except ValueError:
            #field name not found in recs.  must be a missing value
            newrecs[field] = mdict[field]

    return newrecs



def read_flatfile(file_ish, meta, structure):
    """
    Read formatted flat file with known schema objects.

    Parameters
    ----------
    file_ish: str of file-like object
        Fixed-width text file.
    meta: sqlalchemy.MetaData 
        Columns in tables must have info['dtype'] and info['width']
    structure: iterable of str
        The structure of the text file.  Strings are known schema objects 
        (tables, columns).  Duplicate column names will be overwritten!
    
    Returns
    -------
    numpy.rec.array of np.records

    Notes
    -----


    """
    isFileString = isinstance(file_ish, str)

    #prepare for numpy.genfromtxt
    fields, dtypes = get_infovals(meta, structure, 'dtype')
    dtp = np.dtype(zip(fields, dtypes))

    fields, widths = get_infovals(meta, structure, 'width')
    widths = np.array(widths) + 1
    widths[-1] -= 1

    # read the file into a record array
    # try a series of lddate converters
    #1) Anything UTCDateTime can chomp on (which is a lot)
    #2) e.g. '07-JUL-10'
    # TODO: this is kinda hackish
    for conv in [lambda x: UTCDateTime(x).datetime, 
                 lambda x: UTCDateTime().strptime(x, '%d-%b-%y').datetime]:
        try:
            rec = np.genfromtxt(file_ish, usemask=False, autostrip=True, 
                    names=fields, dtype=dtp, delimiter=widths, 
                    converters={'lddate': conv})
            break
        except (TypeError, ValueError) as e:
            #wrong lddate converter
            pass

    #make sure you return a numpy.recarray of records (i.e. type(rec[0]) is numpy.rec.record)
    #rec = np.rec.array(rec.copy()) #works with genfromtxt, unless fields are objects (e.g. datetime)
    rec = format_records(rec, meta, structure) 
    
    return rec


