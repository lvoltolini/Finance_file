from Module import os, sys
from Module import pd, np, plt, sns, sm, ln, dt
from Module import yf, investpy, sgs

'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Info_database # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

extra_phrases = {
    'ret' : 'Retorno\ndo fechamento\nem 1 dias\nEm moeda orig\najust p/ prov\n',
    'price' : 'Retorno\ndo fechamento\nem 1 dias\nEm moeda orig\najust p/ prov\n'
}
    
def to_float(df):
    # Modifica i dati da string a float
    df = df.apply(pd.to_numeric, errors='coerce')
    return df

def new_pct(df):
    # Simile a pct_change, ma include il primo valore se la df é nel formato giusto
    first_row = df.iloc[0] -1
    df = df.pct_change()
    df.iloc[0] = first_row
    
    return df

'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Dates # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

# Important dates:
previous_day, next_day = '2014-04-30', '2022-09-01'
start_date, end_date = '2014-05-02', '2022-09-01'
mid_date = '2015-05-02'
midmid_date = '2016-05-02'

def select_dates(df):
    # Fissa la data
    
    df.index = pd.to_datetime(df.index)
    
    df = df.loc[previous_day: next_day, :]
    
    return df

def lock_dates(df):
    # Fissa la data
    
    df.index = pd.to_datetime(df.index)
    
    df = df.loc[start_date: end_date, :]
    
    return df

'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Reading the files # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

def read_Economatica(path: str, price_ret: str, index = [0], row = [3]):
    
    # Legge il df
    
    df = pd.read_excel(path, index_col = index, header = row)
    
    # Fissa la data
    
    df = select_dates(df)
    
    # Ci sono due tipi di df, con nomi differenti nelle colonne. A seconda del file, cambiamo i nomi delle colonne.
    
    extended_phrase = extra_phrases[price_ret]
    
    # Rinomina le colonne
    
    new_columns = {col: col.replace(extended_phrase, '') for col in df.columns}
    df = df.rename(columns=new_columns)
    
    # Sostituisci i valori '-' per nan
    
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # dropna()
    
    df = df.dropna(how = 'all')

    return df

# Economatica:

raw_path = f'{os.getcwd()}//Raw//'
raw_path_files = [raw_path + i for i in os.listdir(raw_path)]
raw_path_files
  
## Prendre i prezzi ed i ritorni

price = [path for path in raw_path_files if 'price' in path]
ret = [path for path in raw_path_files if 'ret' in path]

## Rinomiare gli df

p21, p22, p41 = (
    read_Economatica(price[0], 'price'), 
    read_Economatica(price[1], 'price'), 
    read_Economatica(price[2], 'price')
)

r21, r22, r41 = (
    read_Economatica(ret[0], 'ret'), 
    read_Economatica(ret[1], 'ret'), 
    read_Economatica(ret[2], 'ret')
)

# Nefin: 

urls = [
    'http://nefin.com.br/resources/risk_factors/Market_Factor.xls',
    'http://nefin.com.br/resources/risk_factors/SMB_Factor.xls',
    'http://nefin.com.br/resources/risk_factors/HML_Factor.xls',
    'http://nefin.com.br/resources/risk_factors/WML_Factor.xls',
    'http://nefin.com.br/resources/risk_factors/IML_Factor.xls',
    'http://nefin.com.br/resources/risk_factors/Risk_Free.xls'
]

# def merge_nefins(urls):
#     nefins = [pd.read_excel(url) for url in  urls]

# def merge_nefins(urls):
#     """
#     Questa funzione riceve una lista di URL e ritorna un dataframe unito sulle colonne ['year', 'month', 'day'].
#     """
#     # leggere tutti i file Excel e creare una lista di df
#     nefins = [pd.read_excel(url) for url in urls]

#     # unire tutti gli df
#     merged_df = pd.concat(nefins, sort=False).reset_index(drop=True)
#     merged_df = merged_df.groupby(['year', 'month', 'day']).mean().reset_index()

#     return merged_df

def merge_nefins(urls):
    """
    Questa funzione riceve una lista di URL e ritorna un dataframe unito sulle colonne ['year', 'month', 'day'].
    """
    # leggere tutti i file Excel e creare una lista di df
    nefins = [pd.read_excel(url) for url in urls]

    # unire tutti gli df
    merged_df = nefins[0]  # inizializzare il dataframe di merge con il primo dataframe nella lista
    for i in range(1, len(nefins)):
        merged_df = pd.merge(merged_df, nefins[i], on=['year', 'month', 'day'])

    # Fissare la data:
    
    merged_df.index = pd.to_datetime(merged_df[['year', 'month', 'day']])
    
    # Drop the columns ['year', 'month', 'day']
    
    merged_df.drop(columns = ['year', 'month', 'day'], inplace = True)
    
    # Fissare la data nel periodo corretto
    
    merged_df = select_dates(merged_df)
    
    # Ora includiamo gli altri df:
    
    ## df esg
    esg = pd.read_excel('Raw//BR_ESG.xls', index_col = [0], header = [6]).iloc[:-1]
    esg.columns = ['esg']
    esg = new_pct(esg/100) # Divide by 100 for the initial value is for reference.
    esg = select_dates(esg)
    
    ## df ibovespa
    ibov = yf.download('^BVSP')['Adj Close']
    ibov = pd.DataFrame(ibov)
    ibov.columns = ['ibov']
    ibov = new_pct(ibov.sort_index())
    ibov = select_dates(ibov)
    
    merged_df = pd.concat(
        [
            merged_df, esg, ibov
        ],
        axis = 1
    )
    
    return merged_df


nefin = merge_nefins(urls)

