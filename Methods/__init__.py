from Module import os, sys
from Module import pd, np, plt, sns, sm, ln, dt
from Module import yf, investpy, sgs

from . import OLS


'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Creazione delle cartelle # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

# ottieni il percorso assoluto della directory che contiene lo script principale
dir_path = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(dir_path)

# imposta la directory di lavoro corrente sulla directory che contiene lo script principale
os.chdir(parent_dir)

# Nomi delle cartelle:

folders = [
    '//Regression//',
    '//Regression//D//',
    '//Regression//M//',
    '//Regression//4M//',
    '//Regression//Y//',
]

subfolders = ['ret//', 'exp//', 'fac//']

# Creazione di una lista di cartelle:

for folder in folders[1:]:
    for subfolder in subfolders:
        folders.append(folder + subfolder)
        # I dati verrano creati anche per le Stock separate
        if subfolder in subfolders[1:]:
            folders.append(folder + subfolder + 'Stocks//')
        
folders.sort()

def Create_folder(path):
    full_path = os.getcwd() + path
    if not os.path.exists(full_path):
        os.makedirs(full_path)

for path in folders:
    Create_folder(path)
    
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Info_database # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

extra_phrases = {
    'ret' : 'Retorno\ndo fechamento\nem 1 dias\nEm moeda orig\najust p/ prov\n',
    'price' : 'PU\najust p/ prov\nEm moeda orig\n'
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

def intersection(x: list, y: list):
    # Restituisce l'intersezione di due liste
    return [item for item in x if item in y]

def resample_returns(df, period:str):
    # Funziona solo per "raggruppare" i dati (da giornaliero a mensile, da giornaliero ad annuale), 
    # non per "dividere" (da annuale a mensile, da mensile a giornaliero).
    "Monthly: 'M'"
    "Quadrimester: '4M'"
    df1 = df.copy()
    df1 = df1+1
    df1 = df1.resample(period).prod()
    df1 = df1 - 1
    return df1

'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Dates # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

# Important dates:
previous_day, next_day = '2014-04-30', '2022-09-01'
start_date, end_date = '2014-05-02', '2022-08-31'
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

def add_year(date, add = 0):
    # Aggiunge un anno alla data
    new_date = dt.date(
        date.year,
        date.month,
        date.day
    ) + dt.timedelta(days = 365 + add)
    return new_date

def rem_year(date, add = 0):
    # Rimuove un anno dalla data
    new_date = dt.date(
        date.year,
        date.month,
        date.day
    ) + dt.timedelta(days = -365 + add)
    return new_date

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

def added_minus(df):
    
    # Creare una coppia di df
    df1 = df.copy()
    
    # Creare le colonne
    df1['ibov_minus_Rf'] = df1['ibov'] - df['Risk_free']
    df1['esg_minus_Rf'] = df1['esg'] - df['Risk_free']
    df1['Rm'] = df1['Rm_minus_Rf'] + df1['Risk_free']
    
    # Creare le colonne per gli altri dati.
    df1['r_ibov_minus_Rf'] = -1 + (df1['ibov']+1)/(df['Risk_free']+1)
    df1['r_esg_minus_Rf'] = -1 + (df1['esg']+1)/(df['Risk_free']+1)
    df1['r_Rm'] =  -1 + (df1['Rm_minus_Rf'] + 1)*(df1['Risk_free'] + 1)
    
    return df1

'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Important Parameters: # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

# Dates
date_format = '%Y-%m-%d'

# Economatica:

raw_path = f'{os.getcwd()}//Raw//'
raw_path_files = [raw_path + i for i in os.listdir(raw_path)]
raw_path_files
  
## Prendre i prezzi ed i ritorni

price = [path for path in raw_path_files if 'price' in path]
ret = [path for path in raw_path_files if 'ret' in path]

## Rinomiare gli df

p21, p22, p41 = (
    lock_dates(read_Economatica(price[0], 'price')), 
    lock_dates(read_Economatica(price[1], 'price')), 
    lock_dates(read_Economatica(price[2], 'price'))
)

r21, r22, r41 = (
    lock_dates(read_Economatica(ret[0], 'ret')/100), 
    lock_dates(read_Economatica(ret[1], 'ret')/100), 
    lock_dates(read_Economatica(ret[2], 'ret')/100)
)

# Ritorno degli Stocks:

stocks = pd.concat(
    [
        r21, r22, r41
    ], axis = 1
).T.drop_duplicates().T

# df Nefin
nefin = merge_nefins(urls) # Creare lo df
nefin = added_minus(nefin) # Adizionare lo "minus"
nefin = lock_dates(nefin) # Lock the dates to '2014-05-02':'2022-08-31'
nefin = nefin.drop([i for i in nefin.index if i not in stocks.index])

# Betas e nome di Regressioni.
betas = {
    'be1': ['Rm_minus_Rf', 'esg_minus_Rf'],
    'be2': ['Rm_minus_Rf', 'SMB', 'HML', 'esg_minus_Rf'],
    'be3': ['Rm_minus_Rf', 'SMB', 'HML', 'WML', 'IML', 'esg_minus_Rf'],
    'bi1': ['Rm_minus_Rf', 'esg_minus_Rf', 'ibov_minus_Rf'], 
    'bi2': ['Rm_minus_Rf', 'SMB', 'HML', 'esg_minus_Rf', 'ibov_minus_Rf'],
    'bi3': ['Rm_minus_Rf', 'SMB', 'HML', 'WML', 'IML', 'esg_minus_Rf', 'ibov_minus_Rf'],
    'bn1': ['esg_minus_Rf'], 
    'bn2': ['esg_minus_Rf', 'SMB', 'HML'],
    'bn3': ['esg_minus_Rf', 'SMB', 'HML', 'WML', 'IML'], 
    'br1': ['Rm_minus_Rf'],
    'br2': ['Rm_minus_Rf', 'SMB', 'HML'],
    'br3': ['Rm_minus_Rf', 'SMB', 'HML', 'WML', 'IML']
}

regressions = list(betas.keys())

unique_factors = ['HML', 'IML', 'Rm_minus_Rf', 'SMB', 'WML', 'esg_minus_Rf', 'ibov_minus_Rf']

# Approach per matrici di covarianza
approaches = ['amo','led','vec']

# Parametri per gli investitori
parameters = {
    '01' : 0.1,
    '05' : 0.5,
    '07' : 0.7,
    '10' : 1.0,
    '15' : 1.5,
    '30' : 3.0,
    '50' : 5.0,
    '100' : 10.0
}



'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Search: # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

# import json

# keys = {
#     "r": [[0], ["D", "M", "4M", "Y"]],
#     "e": [[0,1], ["D", "M", "4M", "Y"]],
#     "f": [[0,1,2], ["D", "M", "4M", "Y"]]
# }

# with open("search_keys.json", "w") as f:
#     json.dump(keys, f, indent=4)

class search():
    @staticmethod
    def search(ritorno, freq, portfolio, folder = 'reg'):
        parent_dir = os.getcwd()
        dict_names = {
            'f': 'factors.csv',
            'e': 'expected.csv'
        }
        path = f'{parent_dir}//Regression//{freq}//{ritorno}//{dict_names[ritorno]}'
        
        return path

    



'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # OLS: # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'

# Old Version:

# A função de regressão. Vale que:
# - stk é o nome da stock
# - x é o DataFrame que contém os fatores para a regressão
# - y é o retorno excesso da ação
# - betas é o nome das colunas onde estão salvos os fatores
# - reg é a legenda dos fatores (bn1, br3, etc.)
# - folder é a pasta onde serão salvos os arquivos
# - port é o nome do portfólio ao qual pertence a Stock
# - obs é o número de observações que serão necessárias para que seja feito OLS na ação. Exemplo: ações que começam em '2014-05-02' têm valor esperado calculado a partir de '2015-05-02'
# - janela = 'expansao' ou 'movel'. Precisa ser decidido para ver se o OLS olha em janela em expansão ou móvel.
# - show pode assumir outros valores caso não se deseje salvar a OLS.
# - last_date_to_try é a data limite para fazer o OLS.
# - d_input = False ou True. Se True, cada novo dia calculado vai mostrar os dados da OLS.



def ols_shift(stk,
              x,
              y,
              betas,
              reg,
              folder,
              port,
              obs = 365,
              janela = 'expansao',
              show = 'save',
              last_date_to_try = '2022-08-31',
              d_input = False):
    
    # Para não aparecer aviso:
    import warnings
    warnings.filterwarnings('ignore')
    
    # Para acompanhar o andamento na tela:
    from IPython.display import clear_output
    
    # Checando se y é caminho ou tabela e dando shift no x:
    y = y[stk][:last_date_to_try]
    x = x.shift().dropna()[:last_date_to_try]
    
    
    # Mantendo índices iguais
    
    save_index = intersection(x.index, y.index)
    ols_index = intersection(x.index, y.dropna().index)
    
    print(ols_index)
    
    if ols_index == []:
        return
    print('ols', ols_index[0])
    print('ols', ols_index[-1])
    
    # Retirando valores Nan
    
    starting_obs = ols_index[0]
    starting_reg = add_year(starting_obs, add = obs-365)
    
    print('starting_obs : ', starting_obs)
    print('starting_reg : ', starting_reg)
    
    # Fixando amostra
    y = y.loc[ols_index]
    x = x.loc[ols_index]
    
    am = y[starting_reg:].index
    if len(am) == 0:
        return
    
    # Deixando ao menos obs = 365 observacoes
    
        
    renew_index(x)
    x = x[starting_obs:]
    
    # Criando lista de fatores e tabela de Expected
    factors = [pd.DataFrame(np.nan, columns = betas[i], index = save_index) for i in range(len(betas))]
    expected = pd.DataFrame(np.nan, columns = reg, index = save_index)

    # Iniciando a Regression - Tela DEBUG
    for i in am:        
        
        # Iniciando a Regression
        for j in range(len(betas)):
            clear_output(wait=True)
            print('------------------------------------------------')
            print(port)
            #print(f'{} out of {} Stocks')
            print(stk)
            print(i)
            if d_input:
                print('y.loc[:i].index (start-end): \n', y.loc[:i].iloc[:-1].index[[0,-1]])
                print('x.loc[:i].index (start-end) lembrando que x = x.shift().dropna()[:last_date_to_try]: \n', x.loc[:i][betas[j]].iloc[:-1].index[[0,-1]])
                print('j, i ', j, i)
                print('expected: ', expected.loc[i])
                input('Pressione uma tecla para a próxima acao: ')
            capm = lm.OLS(y.loc[:i].iloc[:-1], x.loc[:i][betas[j]].iloc[:-1], hasconst = bool).fit()
            factors[j].loc[i] = capm.params
            expected[reg[j]].loc[i] = (capm.params * x[betas[j]].loc[i]).sum() 

        if janela == 'movel':
            x = x.iloc[1:]
            y = y.iloc[1:]
        print(capm.params, flush = True)

    if show == 'save':
        pd.concat(
            factors, keys = reg, axis = 1
        ).to_csv(
            f'{folder}//Fatores//Stocks//fac_shif_{janela[:3]}_{stk}.csv' #_{port}_{stk}.csv'
        )

        expected.to_csv(
            f'{folder}//Expected//Stocks//exp_shif_{janela[:3]}_{stk}.csv' #_{port}_{stk}.csv'
        )
    else: return{
        'fac' : factors,
        'exp' : expected,
        'y' : y
    }[show]


    
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
' # Efficient Frontier: # '
'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'