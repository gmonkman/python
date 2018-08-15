# pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled,not-context-manager, unused-import, undefined-variable, no-member
'''routines to manipulate array like objects like lists, tuples etc'''
import pandas as _pd
import numpy as _np

from funclib.baselib import list_flatten as _list_flatten
from funclib.iolib import wait_key
from funclib.iolib import PrintProgress

# region Pandas


def pd_df_to_ndarray(df):
    '''(dataframe)->ndarray
    Return a dataframe as a numpy array
    '''
    return df.as_matrix([x for x in df.columns])


def col_append(df, col_name):
    '''(df,str)->df
    df is BYREF
    adds a column to dataframe filling it
    with np.NaN values.
    '''
    df.loc[:, col_name] = _pd.Series(_pd.np.nan, index=df.index)


def col_append_nan_fill(df, col_name):
    '''(df,str)->df
    df is BYREF
    adds a column to dataframe filling it
    with np.NaN values.
    '''
    col_append(df, col_name)


def col_append_fill(df, col_name, f):
    '''(df,str,any)->df
    df is BYREF
    adds a column to dataframe filling it with value f
    If f is None, filled with NaN
    '''
    if f is None:
        df.loc[:, col_name] = _pd.Series(_pd.np.nan, index=df.index)
    else:
        df.loc[:, col_name] = _pd.Series(f, index=df.index)


def col_append_rand_fill(df, col_name, lower=0, upper=1):
    '''(df,str,any)->df
    df is BYREF
    adds a column to dataframe filling it with random values from a standard normal
    '''
    df[col_name] = _np.random.choice(range(lower, upper), df.shape[0])


def col_calculate_new(df, func, new_col_name, *args, progress_init_msg='\n'):
    '''(pd.df, function, str, the named arguments for function)
    1) Adds a new column called col_name
    2) calls func with args by position,  where args are the row indices for the values
    3) Row indexes are ZERO based
    4) Consider using apply or similiar for simple use cases

    df = pd.dataframe({'a':[1,2],'b'=[10,20]})

    DF=
    a   b
    1   10
    2   20

    def f(a, b):
        return a*b

    func = f
    col_calculate_new(df, func, 'product', 0, 1)

    DF=
    a   b   product
    1   10  10
    2   20  40
    '''
    assert isinstance(df, _pd.DataFrame)
    if new_col_name in df.columns:
        raise BaseException('Column %s already exists in the dataframe.' % (new_col_name))
    col_append(df, new_col_name)

    args = list(args)
    args = _list_flatten(args)
    PP = PrintProgress(len(df.index), init_msg=progress_init_msg)
    for i, row in df.iterrows():
        PP.increment()
        rowvals = []
        for x in args:
            if row[x] is None:
                vv = None
            elif _np.isnan(row[x]):
                vv = None
            else:
                vv = row[x]
            rowvals.append(vv)
        v = func(*rowvals)
        df.set_value(i, new_col_name, v)


def col_exists(df, col_name):
    '''(str)->bool
    '''
    return col_name in df.columns


def col_index(df, col_name):
    '''(df, str)->int
    Given col return index
    Returns None if doesnt exist
    '''
    if col_exists(df, col_name):
        return df.columns.get_loc(col_name)
    return None


def cols_get_indexes_from_names(df, *args):
    '''df, str args->tuple
    Given list if strings get the corresponding
    column indexes and return as a tuple
    '''
    return [col_index(df, x) for x in args]


def readfld(v, default=None):
    '''return default if v is a pandas null
    '''
    return default if _pd.isnull(v) else v
# endregion
