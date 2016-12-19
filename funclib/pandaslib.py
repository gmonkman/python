#pylint: disable=C0302, too-many-branches, dangerous-default-value, line-too-long, no-member, expression-not-assigned, locally-disabled, not-context-manager, unused-import, undefined-variable
'''routines to manipulate array like objects like lists, tuples etc'''
import pandas as pd
import numpy as np

#region Pandas
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
    df.loc[:, col_name] = pd.Series(pd.np.nan, index=df.index)

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
        df.loc[:, col_name] = pd.Series(pd.np.nan, index=df.index)
    else:
        df.loc[:, col_name] = pd.Series(f, index=df.index)

def col_append_rand_fill(df, col_name):
    '''(df,str,any)->df
    df is BYREF
    adds a column to dataframe filling it with random values from a standard normal
    '''
    df.assign(colname=pd.np_array_datetime64_compat. np.random.randn())

def col_calculate_new(df, func, new_col_name, *args):
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
    col_calculate_new(df, f, 'product', 0, 1)

    DF=
    a   b   product
    1   10  10
    2   20  40
    '''
    assert isinstance(df, pd.DataFrame)
    if new_col_name in df.columns:
        raise BaseException('Column %s already exists in the dataframe.' % (new_col_name))
    col_append(df, new_col_name)

    #
    for i, row in df.iterrows():
        rowvals = [row[x] for x in args]
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
    else:
        return None

def cols_get_indexes_from_names(df, *args):
    '''df, str args->tuple
    Given list if strings get the corresponding
    column indexes and return as a tuple
    '''
    return [col_index(df, x) for x in args]

def readfld(v, default=None):
    '''return default if v us a pandas null
    '''
    return default if pd.isnull(v) else v
#endregion
