# Questo file contiene le funzioni per la regressione utilizzate nella dissertazione.

import pandas as pd
import numpy as np
import statsmodels.regression.linear_model as lm
import os
import sys
from IPython import get_ipython

# Verifica se l'interprete corrente è IPython
if 'ipykernel' in sys.modules:
    # Se siamo in un notebook, importiamo IPython.display.clear_output
    from IPython.display import clear_output
else:
    # Se siamo in un programma, importiamo os.system('cls')
    def clear_output():
        os.system('cls' if os.name == 'nt' else 'clear')

def search(ret, freq):
    ret_dict = {
        'f': ['fac', 'factors'],
        'e': ['exp', 'expected']
    }
    path = f'{os.getcwd()}//Regression//{freq}//{ret_dict[ret][0]}//{ret_dict[ret][1]}.parquet'
    df = pd.read_parquet(path)
    return df


class OLS:
    # @staticmethod
    # def create_df_factors(index, betas):
    #     # Creazione delle tuple per le colonne del dataframe
    #     tuples_columns = [(reg, beta) for reg in betas.keys() for beta in betas[reg]]
    #     # Creazione del dataframe vuoto
    #     df = pd.DataFrame(np.nan, index=index, columns=pd.MultiIndex.from_tuples(tuples_columns))
    #     return df

    @staticmethod
    def create_df_factors(index, betas):
        """
        Funzione che crea un dataframe vuoto con colonne
        date dal dict betas.
        """
        tuples_columns = [(reg, beta) for reg in betas.keys() for beta in betas[reg]]
        df = pd.DataFrame(np.nan, index=index, columns=pd.MultiIndex.from_tuples(tuples_columns))
        return df
    
    @staticmethod
    def preprocess_data(X, Y, freq):
        """
        Funzione che fa la resampling dei dati non giornalieri e
        restituisce i dati dopo lo shift.
        """
        from Methods import resample_returns
        if freq != 'D':
            X = resample_returns(X, freq)
            Y = resample_returns(Y, freq)
        X = X.shift().dropna()
        return X, Y

    @staticmethod
    def filter_valid_indices(X, Y):
        """
        Funzione che filtra gli indici di Y che non sono presenti in X.
        """
        from Methods import intersection, add_year
        # Salviamo l'indice
        stk = Y.name
        save_index = intersection(X.index, Y.index)
        ols_index = intersection(X.index, Y.dropna().index)
        
        # Ora impostiamo i dati
        X = X.loc[ols_index]
        Y = Y.loc[ols_index]
        starting_valid_obs = add_year(ols_index[0])
        
        # Reimpostiamo l'indice:
        ols_index = X.loc[starting_valid_obs: , :].index
        
        return save_index, ols_index, X, Y, stk

    @staticmethod
    def print_debug_info(stk, regression_name, date, betas):
        clear_output()
        div = 50*'-'
        print(div, 
            stk, 
            regression_name, 
            date, 
            div, 
            sep = '\n')

    @staticmethod
    def run_ols(X, Y, betas, date, regression_name, pause):
        """
        Funzione che esegue la regressione OLS e restituisce il risultato.
        """
        capm = lm.OLS(
            Y.loc[:date].iloc[:-1], 
            X.loc[:date, betas[regression_name]].iloc[:-1], 
            hasconst=True).fit()
        if pause:
            div = 50*'-'
            print(div, 
                'date saved on factors: ', date,
                'y.loc[:i].index (start-end):', Y.loc[:date].iloc[:-1], 
                'x.loc[:i].index (start-end) lembrando que x = x.shift().dropna()[:last_date_to_try]:', X.loc[:date, betas[regression_name]].iloc[:-1], 
                sep = '\n')
            input('Pressione uma tecla para a próxima acao: ')
        return list(capm.params)

    @staticmethod
    def ols(X, Y, betas: dict, freq='D', pause=False):
        """
        Funzione che esegue la regressione OLS su Y rispetto ad X
        in base ai beta passati come dict.
        """
        # Attention to avoid circular imports
        
        # Preprocessing dei dati
        X, Y = OLS.preprocess_data(X, Y, freq)

        # Filtraggio degli indici validi
        save_index, ols_index, X, Y, stk = OLS.filter_valid_indices(X, Y)
        
        # Inizializzazione del dataframe dei fattori
        factors = OLS.create_df_factors(ols_index, betas)

        for date in ols_index:
            clear_output()
            div = 50*'-'
            print(div, 
                stk, 
                date, 
                div, 
                sep = '\n')
            
            for regression_name in list(betas.keys()):
                # Debug INFO
                # OLS.print_debug_info(stk, regression_name, date, betas)
                
                # Esecuzione della regressione OLS
                capm_params = OLS.run_ols(X, Y, betas, date, regression_name, pause)

                # Aggiornamento del dataframe dei fattori
                factors.loc[date, (regression_name, betas[regression_name])] = capm_params
                
                # print('factors', factors.loc[date, (regression_name, betas[regression_name])])
                # print('capm', capm_params)
                # input('olhe')

        # Restituzione del dataframe dei fattori
        # return factors.iloc
        path = f'{os.getcwd()}//Regression//{freq}//fac//Stocks//{stk}.csv'
        factors.to_csv(path)
    
    @staticmethod
    def start_regression(X: pd.DataFrame, stocks: pd.DataFrame, betas: dict, freq: str):
        # Esegue la regressione lineare per ogni azione
        for stock in stocks.columns:
            OLS.ols(X, stocks[stock], betas, freq = freq)
            
    @staticmethod
    def merge_factors(freq):
        # Ottiene il percorso della directory contenente i dati sui fattori di frequenza specificata
        path = f'{os.getcwd()}//Regression//{freq}//fac//Stocks//'
        # Ottiene il percorso della directory padre dei dati sui fattori di frequenza specificata
        parent_path = f'{os.getcwd()}//Regression//{freq}//fac//'
        
        # Ottiene i nomi dei file dei fattori di ogni azione nella directory dei dati sui fattori di frequenza specificata
        factors_of_stocks = [
            filename[:-4] for filename in os.listdir(path)
        ]
        
        # Ottiene i dati sui fattori per ogni azione e li inserisce in una lista
        list_of_factors_by_stock = [
            pd.read_csv(path + filename + '.csv', index_col = [0], header = [0,1])
            for filename in factors_of_stocks
        ]
        
        # Concatena tutti i dati sui fattori in un unico DataFrame
        df = pd.concat(list_of_factors_by_stock, axis = 1, keys = factors_of_stocks)
        
        return df
    
    @staticmethod
    def save_factors(df, freq):
        # Ottiene il percorso della directory contenente i dati sui fattori di frequenza specificata
        dac_path = f'{os.getcwd()}//Regression//{freq}//fac//'
        
        # Salva il DataFrame dei fattori in formato Parquet nella directory dei dati sui fattori di frequenza specificata
        df.to_parquet(f'{dac_path}factors.parquet')
    
    def save_expected(factors, indices, freq):
        # Copia gli indici e i fattori e modifica il formato degli indici in formato datetime
        indices, factors = indices.copy(), factors.copy()
        indices.index, factors.index = pd.to_datetime(indices.index), pd.to_datetime(factors.index)
        
        # Resample i ritorni:
        if freq != 'D':
            from Methods import resample_returns
            indices = resample_returns(indices, freq)
        # Sposta gli indici di un giorno in avanti e seleziona solo gli indici corrispondenti ai dati sui fattori
        indices = indices.shift().loc[factors.index]
        factors = factors.loc[indices.index]
        
        # Imposta l'indice dei fattori come l'indice degli indici
        factors.index = indices.index
        
        # Moltiplica ogni valore dei fattori per il valore corrispondente degli indici
        df = factors.multiply(indices, level = 2)
        
        # Somma i valori dei fattori per ogni coppia di (data, azione) e salva il risultato in un DataFrame
        df_sum = df.groupby(level = [0,1], axis = 1).sum()
        
        # Salva il DataFrame dei fattori attesi in formato Parquet nella directory dei dati sui fattori di frequenza specificata
        exp_path = f'{os.getcwd()}//Regression//{freq}//exp//'
        df_sum.to_parquet(f'{exp_path}expected.parquet')
    
    @staticmethod
    def SAVE_ALL_ITEMS_IN_OLS(X, Y, betas, freq):
        # First, we calculate and separate each factor from each stock separatedly:
        OLS.start_regression(X, Y, betas, freq  = freq)
        # Then we merge all of them into a single file:
        OLS.save_factors(
                         OLS.merge_factors(freq),
                         freq
                         )
        # Now we calculate expected values of stocks:
        OLS.save_expected(
            search('f', freq),
            X,
            freq)
    
    
    @staticmethod
    def DEBUG_OLS_INFO():
        # Stampa un messaggio di debug sulla regressione
        div = 80*'-'
        print(
            div,
            'La Regressione sta per avviare. Continua? [S/n]: ', 
            div, sep = '\n')
        return input('Risposta: ')
    
    @staticmethod
    def DEBUG_FIX_FACTORS_AND_EXPECTED():
        # Stampa un messaggio di debug sulla regressione
        div = 80*'-'
        print(
            div,
            'Il programma sta per avviare la  Continua? [S/n]: ', 
            div, sep = '\n')
        return input('Risposta: ')





    # @staticmethod
    # def merge_factors(freq):
    #     path = f'{os.getcwd()}//Regression//{freq}//fac//Stocks//'
    #     parent_path = f'{os.getcwd()}//Regression//{freq}//fac//'

    #     factors_of_stocks = [
    #         filename[:-4] for filename in os.listdir(path)
    #     ]

    #     list_of_factors_by_stock = [
    #         pd.read_csv(path + filename + '.csv', index_col = [0], header = [0,1])
    #         for filename in factors_of_stocks
    #     ]

    #     df = pd.concat(list_of_factors_by_stock, axis = 1, keys = factors_of_stocks)
        
    #     return df
    
    # @staticmethod
    # def save_factors(df, freq):
    #     dac_path = f'{os.getcwd()}//Regression//{freq}//fac//'
    #     df.to_parquet(f'{dac_path}factors.parquet')
    
    # def save_expected(factors, indices, freq):
    #     indices, factors = indices.copy(), factors.copy()
    #     indices.index, factors.index = pd.to_datetime(indices.index), pd.to_datetime(factors.index)
    #     indices = indices.shift().loc[factors.index]
    #     factors = factors.loc[indices.index]
    #     factors.index = indices.index
    #     df = factors.multiply(indices, level = 2)
    #     df_sum = df.groupby(level = [0,1], axis = 1).sum()
    #     clear_output()
    #     print(df_sum)
    #     exp_path = f'{os.getcwd()}//Regression//{freq}//exp//'
    #     df_sum.to_parquet(f'{exp_path}expected.parquet')
    
    # def show_expected(factors, indices):
    #     indices = indices.shift().loc[factors.index]
    #     factors = factors.loc[indices.index]
    #     factors.index = indices.index
    #     df = pd.DataFrame(np.nan, index = indices.index, columns = factors.columns)
    #     for column in factors.columns:
    #         if column[2] in indices.columns:
    #             clear_output()
    #             print(80*'-')
    #             print(column)
    #             print(80*'-')
    #             df.loc[:, column] = factors[column].multiply(indices[column[2]])
    #     return df
    # @staticmethod
    # def start_regression(X: pd.DataFrame, stocks: pd.DataFrame, betas: dict, freq: str):
    #     for stock in stocks.columns:
    #         OLS.ols(X, stocks[stock], betas, freq = freq)
        
    # @staticmethod
    # def DEBUG_OLS_INFO():
    #     div = 80*'-'
    #     print(
    #         div,
    #         'La Regressione sta per avviare. Continua? [S/n]: ', 
    #         div, sep = '\n')
    #     input('Risposta: ')
    
   
