# Questo file contiene le funzioni per il calcolo della frontiera efficiente di Markowitz utilizzata nella dissertazione.

import pandas as pd
import numpy as np
import importlib
from pypfopt import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
import os
import sys
from IPython import get_ipython
import warnings
import time

# Verifica se l'interprete corrente è IPython
if 'ipykernel' in sys.modules:
    # Se siamo in un notebook, importiamo IPython.display.clear_output
    from IPython.display import clear_output
else:
    # Se siamo in un programma, importiamo os.system('cls')
    def clear_output():
        os.system('cls' if os.name == 'nt' else 'clear')

# # Importiamo gli df
# from Methods import r21, r22, r41, betas, approaches, parameters, window, portfolios

# La class che contiene le funzioni per lavorare con i portafolgi.
class Portfolios():
    
    @staticmethod
    def select_variables(portfolio):
        # Scegliamo il portafoglio
        portfolio = importlib.import_module(f"Methods.{portfolio}")
        # Importiamo gli df
        from Methods import portfolio, betas, approaches, parameters, window, portfolios
        
        return portfolio, betas, approaches, parameters, window, portfolios

    # @staticmethod
    # def covariance(df: pd.DataFrame, type_covariance: str, window: str, name_cov: str = 'constant_variance'):
        
    #     if window == 'Mov':
    #         # seleziona solo l'ultimo anno di dati
    #         last_year = df.index[-1] - pd.DateOffset(years=1)
    #         df = df.loc[last_year:]
        
    #     if type_covariance == 'amo':
    #         # calcola la Sample matrice di covarianza
    #         return df.cov()
        
    #     elif type_covariance == 'led':
    #         # Calcola la matrice di covarianza con il metodo Ledoit-Wolf usando pyfopt
    #         shrunk = CovarianceShrinkage(df).ledoit_wolf()
            
    #         if name_cov == 'constant_variance':
    #             # Shrunk covariance matrix - constant variance assumption
    #             return shrunk
    #         elif name_cov == 'diag':
    #             # Diagonal matrix
    #             return shrunk.as_diag()
    #         elif name_cov == 'factor':
    #             # Factor model assumption
    #             return shrunk.as_factor_model()

    
    @staticmethod
    def covariance(df: pd.DataFrame, type_covariance: str, window: str, name_cov: str = 'constant_variance'):
        
        if window == 'Mov':
            # seleziona solo l'ultimo anno di dati
            last_year = df.index[-1] - pd.DateOffset(years=1)
            df = df.loc[last_year:]
        
        if type_covariance == 'amo':
            # calcola la Sample matrice di covarianza
            return df.cov()
        
        elif type_covariance == 'led':
            # Calcola la matrice di covarianza con il metodo Ledoit-Wolf usando pyfopt
            shrunk = CovarianceShrinkage(df).ledoit_wolf()
            
            if name_cov == 'constant_variance':
                # Shrunk covariance matrix - constant variance assumption
                return shrunk
            elif name_cov == 'diag':
                # Diagonal matrix
                return shrunk.as_diag()
            elif name_cov == 'factor':
                # Factor model assumption
                return shrunk.as_factor_model()

    @staticmethod
    def columns_of_Efficient_frontier_portfolios(
        df: pd.DataFrame,
        df_name: str, 
        freq: str,
        betas: dict,
        parameters: dict,
        window: list,
        cov: str        
    ):

        # Creazione di una df senza valori.
        idx = pd.MultiIndex.from_product([
            [df_name], [cov], [freq], window, parameters.keys(), betas.keys()
        ], names=['df_name', 'cov', 'freq', 'window', 'parameters', 'betas'])
        
        ef_df = pd.DataFrame(index=df.index, columns=idx)
        
        return ef_df

    @staticmethod
    def columns_of_Efficient_frontier_weights(
        df: pd.DataFrame,
        df_name: str, 
        freq: str,
        betas: dict,
        parameters: dict,
        window: list,
        cov: str,
        cols: list        
    ):

        # Creazione di una df senza valori.
        idx = pd.MultiIndex.from_product([
            [df_name], [cov], [freq], window, parameters.keys(), betas.keys(), cols
        ], names=['df_name', 'cov', 'freq', 'window', 'parameters', 'betas', 'stocks'])
        
        ef_df = pd.DataFrame(index=df.index, columns=idx)
        
        return ef_df
        
    @staticmethod
    def Efficient_frontier_calculator(
        df: pd.DataFrame,
        df_name: str, 
        freq: str,
        betas: dict,
        parameters: dict,
        window: list,
        cov: str,
        start_date = '2016-05-02'      
    ) -> pd.DataFrame:
    
        warnings.filterwarnings('ignore')
        start = time.time()
        
        from . import Search
        
        # Step 0: Crea una lista con gli index degli errori:
        list_of_errors = dict()
        
        # Step 1: Carica il df con i valori attesi per ogni azione in ogni data
        expected = Search.search('e', freq).loc[:, df.columns].reorder_levels([1,0], axis = 1)
        expected.index = pd.to_datetime(expected.index)
        
        # Step 2: Crea un MultiIndex vuoto con le informazioni richieste
        results_df = Portfolios.columns_of_Efficient_frontier_weights(df,
                                                    df_name,
                                                    freq,
                                                    betas,
                                                    parameters, 
                                                    window,
                                                    cov,
                                                    df.columns)
        # print(results_df)
        # Loop over each day in the index
        for date in df.loc[start_date:].index:
            # Slice the DataFrame to only include data up to the current date
            df_sliced = df.loc[:date]
            # Check which stocks have expected values for this day
            available_stocks = expected.loc[date, 'be1'].dropna().index

            # Step 3: Loop over each combination of window, parameter and beta
            for w in window:
                # Calcoliamo la matrice di covarianza
                cov_matrix = Portfolios.covariance(df_sliced[available_stocks].iloc[:-1], cov, w)
        
                clear_output()
                print(
                    80*'-', 
                    date,
                    w,
                    time.time() - start,
                    80*'-',
                    sep = '\n'
                )
                        
                for parameter in parameters.keys():
                    for beta in betas.keys():
                        
                        # Get expected returns for current beta
                        expected_returns_b = expected.loc[date, beta][available_stocks]
                        
                        # Create EfficientFrontier object and calculate max utility
                        try: 
                            ef = EfficientFrontier(expected_returns_b, cov_matrix)
                            ef.add_constraint(lambda w: sum(w) == 1)
                            # ef.max_quadratic_utility(risk_aversion = parameters[parameter])
                            # max_utility = ef.portfolio_performance()[2]
                            # weights = ef.clean_weights()
                            weights = ef.max_quadratic_utility(risk_aversion = parameters[parameter])
                        except: list_of_errors[(df_name, cov, freq, w, parameter, beta)] = [date]
                        # # Store results in dataframe
                        else: 
                            for key in weights.keys(): # For some reason, results_df.loc[date, (df_name, cov, freq, w, parameter, beta)] = weights doesn't work.
                                results_df.loc[date, (df_name, cov, freq, w, parameter, beta, key)] = weights[key]
                        # results_df.loc[(w, parameter, beta), 'max_utility'] = max_utility
                        # results_df.loc[(w, parameter, beta), 'portfolio_weights'] = weights
        list_of_errors = pd.DataFrame(list_of_errors)
        return results_df, list_of_errors

    @staticmethod
    def save_efficient_frontier_calculations(
        df: pd.DataFrame,
        df_name: str, 
        freq: str,
        betas: dict,
        parameters: dict,
        window: list,
        cov: str        
    ):
        df_eff, df_errors = Portfolios.Efficient_frontier_calculator(
            df,
            df_name, 
            freq,
            betas,
            parameters,
            window,
            cov  
        )
        weights_name = f'{os.getcwd()}//Portfolios//eff_{df_name}_{freq}_{cov}.parquet'
        errors_name = f'{os.getcwd()}//Errors//err_{df_name}_{freq}_{cov}.parquet'
        df_eff.to_parquet(weights_name)
        df_errors.to_parquet(errors_name)
        
    @staticmethod
    def DEBUG_EFF_INFO():
        # Stampa un messaggio di debug sulla regressione
        div = 80*'-'
        print(
            div,
            'Il Calcolo della Efficient frontier sta per avviare. Continua? [S/n]: ', 
            div, sep = '\n')
        return input('Risposta: ')
    # Example:
    # df = Efficient_frontier_calculator(
    #     resample_returns(r21, 'M'),
    #     'r21', 
    #     'M',
    #     betas,
    #     parameters,
    #     window,
    #     'amo'   
    # )