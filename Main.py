
# Packages:
from Module import os, sys # Per la creazione delle cartelle.
from Module import pd, np, plt, sns, sm, ln, dt, lm
from Module import yf, investpy, sgs # Per ottenere i dati online.


# Variabili:
from Methods import p21, p22, p41, r21, r22, r41, stocks # dfs
from Methods import nefin, betas, regressions, parameters, approaches, unique_factors # Lists
from Methods import previous_day, next_day, start_date, end_date, mid_date, midmid_date # Dates

from Methods.OLS import OLS as OLS # Module per la regressione
from Methods.OLS import search
from Methods import resample_returns, new_pct, add_year, intersection # Funzioni

div = 80 * '-'
freqs= ['D', 'M', '4M', 'Y']

answer_ols_debug_info = OLS.DEBUG_OLS_INFO()
if answer_ols_debug_info == 's':
    for freq in freqs:
        OLS.SAVE_ALL_ITEMS_IN_OLS(nefin, stocks, betas, freq)
elif answer_ols_debug_info in freqs:
    OLS.SAVE_ALL_ITEMS_IN_OLS(nefin, stocks, betas, answer_ols_debug_info)


input('O Programa foi finalizado. Pressione uma tecla para encerrar o programa: ')

'9(HxdwW^vk0XY^nb'