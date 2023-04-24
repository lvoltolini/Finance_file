from Module import *

# def df_str_to_flt(df):
#     df = df.apply(pd.to_numeric, errors='coerce')
#     return df

previous_day, next_day = '2014-04-30', '2022-09-01'

def read_Economatica(path: str, row: int, price_ret: str, index = [0]):
    
    # Creiamo il df
    
    df = pd.read_excel(path, index_col = index, header = [row])
    
    # Fissa la data
    
    df.index = pd.to_datetime(df.index)
    
    df = df.loc[previous_day: next_day, :]
    
    # Ci sono due tipi di df, con nomi differenti nelle colonne. A seconda del file, cambiamo i nomi delle colonne.
    
    if price_ret == 'ret':
        extended_phrase = 'Retorno\ndo fechamento\nem 1 dias\nEm moeda orig\najust p/ prov\n'
    else: extended_phrase = 'Retorno\ndo fechamento\nem 1 dias\nEm moeda orig\najust p/ prov\n'
    
    # Rinomina le colonne
    
    new_columns = {col: col.replace(extended_phrase, '') for col in df.columns}
    df = df.rename(columns=new_columns)
    
    # Sostituisci i valori '-' per nan
    
    df = df.apply(pd.to_numeric, errors='coerce')
    
    return df