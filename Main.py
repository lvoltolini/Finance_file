
# Packages:
from Module import os, sys # Per la creazione delle cartelle.
from Module import pd, np, plt, sns, sm, ln, dt, lm
from Module import yf, investpy, sgs # Per ottenere i dati online.


# Variabili:
from Methods import p21, p22, p41, r21, r22, r41, stocks # dfs
from Methods import nefin, betas, regressions, parameters, approaches, unique_factors # Lists
from Methods import previous_day, next_day, start_date, end_date, mid_date, midmid_date # Dates

from Methods.OLS import OLS as OLS # Module per la regressione

from Methods import resample_returns, new_pct, add_year, intersection # Funzioni

div = 80 * '-'

OLS.DEBUG_OLS_INFO()

OLS.start_regression(nefin, stocks, betas, freq  = 'D')
OLS.start_regression(nefin, stocks, betas, freq  = 'M')
OLS.start_regression(nefin, stocks, betas, freq  = '4M')
OLS.start_regression(nefin, stocks, betas, freq  = 'Y')

input('O Programa foi finalizado. Pressione uma tecla para encerrar o programa: ')

'9(HxdwW^vk0XY^nb'