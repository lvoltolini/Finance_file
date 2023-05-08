# Pacchetti:
from Module import os, sys # Per la creazione delle cartelle.
from Module import pd, np, plt, sns, sm, ln, dt, lm
from Module import yf, investpy, sgs # Per ottenere i dati online.

# Importo le variabili e le funzioni dai moduli che ho creato
from Methods import p21, p22, p41, r21, r22, r41, stocks # dfs
from Methods import nefin, betas, regressions, parameters, approaches, portfolios, freqs, covs, unique_factors, window # Liste
from Methods import previous_day, next_day, start_date, end_date, mid_date, midmid_date # Date
from Methods import resample_returns, new_pct, add_year, intersection, Search # Funzioni

from Methods.OLS import OLS as OLS # Module per la regressione
from Methods.OLS import search

from Methods.Portfolios import Portfolios
# Variabili:

div = 80 * '-'

# # Frequenze dei dati
# freqs= ['D', 'M', '4M', 'Y']


# Chiedo all'utente se vuole avviare la modalità debug della regressione
answer_ols_debug_info = OLS.DEBUG_OLS_INFO()

if answer_ols_debug_info == 's':
    # Salvo tutti i risultati per tutte le frequenze
    for freq in freqs:
        OLS.SAVE_ALL_ITEMS_IN_OLS(nefin, stocks, betas, freq)
elif answer_ols_debug_info in freqs:
    # Salvo tutti i risultati solo per la frequenza specificata
    OLS.SAVE_ALL_ITEMS_IN_OLS(nefin, stocks, betas, answer_ols_debug_info)

# Chiedo all'utente se vuole avviare la modalità debug della Efficient Frontier
answer_eff_debug_info = Portfolios.DEBUG_EFF_INFO()

if answer_eff_debug_info == 's':
    
    # Salvo tutti i risultati per tutte le parameters
    for element in Search.names_for_eff():
        Portfolios.save_efficient_frontier_calculations(
            Search.search(element[0], element[1]),
                        element[0],
                        element[1], 
                        element[2], 
                        element[3], 
                        element[4], 
                        element[5])
        
elif answer_eff_debug_info in portfolios:
    # Salvo tutti i risultati dalle informazioni fornite
    ret = answer_eff_debug_info
    freq = input('Provide una frequenza: ')
    Portfolios.save_efficient_frontier_calculations(
        Search.search(ret, freq),
        ret,
        freq,
        betas,
        parameters,
        window,
        input('Provide una matrice di covarianza: ')
    )
        

# Chiedo all'utente di premere un tasto per terminare il programma
input('O Programa foi finalizado. Pressione uma tecla para encerrar o programa: ')
