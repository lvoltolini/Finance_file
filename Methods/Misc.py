# os pandas warnings Search
import os 
import pandas as pd
import warnings 
import numpy as np
import plotly.express as px 

def eff_weights_dfs(portfolio:str, freq:str, cov:str, folder = 'Raw') -> pd.DataFrame:
    folder = f'{os.getcwd()}//Portfolios//{folder}//'
    
    filename = f'{folder}eff_{portfolio}_{freq}_{cov}.parquet'
    return pd.read_parquet(filename)

def eff_performance_dfs(portfolio:str, freq:str, cov:str, folder = 'Raw') -> pd.DataFrame:
    import warnings
    from Methods import Search
    warnings.filterwarnings('ignore')
    try: df = eff_weights_dfs(portfolio, freq, cov, folder)
    except: print(portfolio, freq, cov)
    cols = df.droplevel('stocks', axis = 1).columns.drop_duplicates()
    index = df.index
    df_returns = pd.DataFrame(np.nan, index = index, columns = cols)
    
    for col in cols:
        df_returns[col] = df[col].multiply(Search.search(portfolio, freq.split('_')[0])).sum(axis = 1)
    return df_returns

def eff_concat_freq(portfolios: list, freq: str, covs: list, folder = 'Raw', name_of_data = 'raw') -> pd.DataFrame:
    from Methods import resample_returns
    
    list_of_dfs = [eff_performance_dfs(
        portfolio, freq, cov, folder
    ) for portfolio in portfolios for cov in covs]
    df = pd.concat(list_of_dfs, axis = 1)
    folder = f'{os.getcwd()}//Portfolios//{folder}//'
    df.to_parquet(f'{folder}portfolios_{name_of_data}_returns_{freq}.parquet')
    ((df+1).cumprod()).to_parquet(f'{folder}portfolios_{name_of_data}_wealth_{freq}.parquet')

def join_column_names(df):
    ds = df.copy()
    if len(ds.columns.levels) > 1:
        ds.columns = ['_'.join(i) for i in ds.columns]
    return ds

def split_column_names(df, level_names = False):
    ds = df.copy()
    if type(df.columns[0]) == str:
        ds.columns = pd.MultiIndex.from_tuples([i.split('_') for i in ds.columns])
    if level_names:
        ds.columns.names = level_names
    return ds

def Mestrado_notation_to_correct_notation(df):
    df1 = df.copy()
    df1 = split_column_names(df)
    try: 
        df1 = df1.reorder_levels([2, 1, 3, 0, 5, 4], axis = 1)
        df1.columns.names = ['df_name', 'cov', 'freq', 'window', 'parameters', 'betas']
    except: 
        df1 = df1.reorder_levels([2, 1, 3, 0, 5, 4, 6], axis = 1)
        df1.columns.names = ['df_name', 'cov', 'freq', 'window', 'parameters', 'betas', 'stocks']
    return df1