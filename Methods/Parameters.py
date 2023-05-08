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

# La finestra di osservazione:
window = ['Mov', 'Exp']

# Portafogli: 
portfolios = ['r21', 'r22', 'r41']