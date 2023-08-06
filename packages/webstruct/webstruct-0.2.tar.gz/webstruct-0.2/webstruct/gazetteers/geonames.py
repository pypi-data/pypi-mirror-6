# -*- coding: utf-8 -*-
from __future__ import absolute_import
import csv
import zipfile
import numpy as np

GAZETTEER_FORMAT = "2s 1s 5s 2s 3s"
GAZETTEER_COLUMNS = ['country_code', 'feature_class', 'feature_code',
                     'admin1_code', 'admin2_code']

_GEONAMES_COLUMNS = ['geonameid', 'main_name', 'asciiname', 'alternatenames',
                     'latitude', 'longitude', 'feature_class',
                     'feature_code', 'country_code', 'cc2',
                     'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code',
                     'population', 'elevation', 'dem', 'timezone',
                     'modification_date']

_GEONAMES_DTYPES = {
    'feature_class': object,
    'feature_code': object,
    'country_code': object,
    'admin1_code': object,
    'admin2_code': object,
    'admin3_code': object,
    'admin4_code': object,
}

_GEONAMES_PANDAS_PARAMS = dict(
    sep='\t',
    header=None,
    encoding='utf8',
    quoting=csv.QUOTE_NONE,
    names=_GEONAMES_COLUMNS,
    dtype=_GEONAMES_DTYPES
)


def to_marisa(df, columns=GAZETTEER_COLUMNS, format=GAZETTEER_FORMAT):
    """
    Encode ``pandas.DataFrame`` with GeoNames data
    (loaded using :func:`read_geonames` and maybe filtered in some way)
    to a ``marisa.RecordTrie``.
    """
    import marisa_trie

    def data_iter(df):
        df = _split_names_into_rows(df)
        for idx, row in df.iterrows():
            yield row['name'], _ensure_utf8([row[c] for c in columns])

    return marisa_trie.RecordTrie(format, data_iter(df))


def read_geonames(filename):
    """
    Parse geonames file to a pandas.DataFrame. File may be downloaded
    from http://download.geonames.org/export/dump/; it should be unzipped
    and in a "geonames table" format.
    """
    import pandas as pd
    return pd.read_csv(filename, **_GEONAMES_PANDAS_PARAMS)


def read_geonames_zipped(zip_filename, geonames_filename):
    """ Parse zipped geonames file. """
    with zipfile.ZipFile(zip_filename, 'r') as zf:
        fp = zf.open(geonames_filename)
        return read_geonames(fp)


def _joined_names_column(df):
    """
    Join data from all name columns into a single column.
    """
    return df.apply(
        lambda row: ','.join(set([
            unicode(n)
            for n in [row['main_name'], row['asciiname'], row['alternatenames']]
            if n and n is not np.nan
        ])),
        axis=1
    )


def _split_names_into_rows(df):
    """
    Create a separate row for each alternate name (with other data duplicated).
    Delete 'main_name', 'asciiname' and 'alternatenames' columns and add
    a single 'name' column instead.
    """
    import pandas as pd

    names = _joined_names_column(df).str.split(',')
    name_lenghts = names.map(len)
    idx = np.repeat(name_lenghts.index, name_lenghts.values)

    names_split = np.concatenate(names.values)
    names_s = pd.Series(names_split, index=idx)
    names_s.name = 'name'

    df = df.join(names_s, )
    del df['main_name']
    del df['asciiname']
    del df['alternatenames']

    cols = df.columns.tolist()
    cols = cols[0:1] + cols[-1:] + cols[1:-1]
    df = df[cols]
    return df.reset_index()


def _ensure_utf8(lst):
    return [v.encode('utf8') if not isinstance(v, float) else str(v)
            for v in lst]
