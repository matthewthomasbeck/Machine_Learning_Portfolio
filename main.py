##################################################################################
# Copyright (c) 2025 Matthew Thomas Beck                                         #
#                                                                                #
# Licensed under the Creative Commons Attribution-NonCommercial 4.0              #
# International (CC BY-NC 4.0). Personal and educational use is permitted.       #
# Commercial use by companies or for-profit entities is prohibited.              #
##################################################################################





############################################################
############### IMPORT / CREATE DEPENDENCIES ###############
############################################################


########## IMPORT DEPENDENCIES ##########

##### handling functions #####

# used to handle a specific financial instrument class
from helper_functions.financial_instruments import handle_stocks
from helper_functions.financial_instruments import handle_agriculture
from helper_functions.financial_instruments import handle_energy
from helper_functions.financial_instruments import handle_fx
from helper_functions.financial_instruments import handle_metal

##### API keys #####

import json # list of all API keys

##### miscellaneous libraries #####

from datetime import datetime as dt # used for discerning timeframe parameters





#######################################################
############### CREATE HELPER FUNCTIONS ###############
#######################################################


########## LOAD API KEYS ##########

def load_api_keys(): # function to load all the current API keys being used

    with open('config.json') as f: # set the json above as a file-like object f and open it

        config = json.load(f) # set config as the json loaded above

    return config # return the config file will all the APIs


########## GET START OF CURRENT QUARTER ##########

def get_quarter_dates(): # function to find the current quarter based on the current date

    ##### calculate current quarter start and end dates #####

    today = dt.now() # grab current day with now function

    # subtract by 1 to 0-based index, floor divide by 3 to get quarter number, multiply by 3 to return to original scale
    # of months, then add 1 to return to 1-based index
    quarterStartMonth = (((today.month - 1) // 3) * 3) + 1

    # find the start date by using the year, the current quarter's beginning month, and the 1st of said month
    currentQuarterStart = str(dt(today.year, quarterStartMonth, 1).date())

    currentQuarterEnd = str(dt.now().date()) # set end of current quarter to be today

    return currentQuarterStart, currentQuarterEnd # return start date of quarter





################################################################
############### COLLECT FINANCIAL INSTRUMENT DATA ##############
################################################################


########## RUN FILES MANUALLY ##########

def run_files_manually(): # function to run files manually during development

    ##### load API keys #####

    apiKeys = load_api_keys() # call loadAPIKeys to get all the necessary API keys
    alphaVantageKey = apiKeys.get('alpha_vantage', {}).get('api_key', None) # grab alpha vantage key
    quandlKey = apiKeys.get('quandl', {}).get('api_key', None) # grab quandl key
    ccxtKey = apiKeys.get('ccxt', {}).get('api_key', None) # grab ccxt key

    ########## create lists of data ##########

    # call getQuarterDates to determine start date at beginning of current quarter, end date current day
    startQuarterDate, endQuarterDate = get_quarter_dates()

    try: # attempt to call handleStocks to neatly take care of stock functions...

        # call handleStocks to update data
        handle_stocks(alphaVantageKey, startQuarterDate, endQuarterDate, False, True, True, False)

    except Exception as e: # if handleStocks fails...

        print(f'Failed to update stock data. Returned with error: "{e}"\n') # print failure statement

    ##### agricultural commodities list #####

    try: # attempt to call handleAgriculture to neatly take care of agriculture functions...

        # call handleAgriculture to update data
        handle_agriculture(quandlKey, startQuarterDate, endQuarterDate, False, False)

    except Exception as e: # if handleAgriculture fails...

        print(f'Failed to update agriculture data. Returned with error: "{e}"\n') # print failure statement

    ##### energy commodities list #####

    try: # attempt to call handleEnergy to neatly take care of energy functions...

        handle_energy(quandlKey, startQuarterDate, endQuarterDate, False, False) # call handleEnergy to update data

    except Exception as e: # if handleEnergy fails...

        print(f'Failed to update energy data. Returned with error: "{e}"\n') # print failure statement

    ##### fx contracts list #####

    try: # attempt to call handleFx to neatly take care of energy functions...

        handle_fx(quandlKey, startQuarterDate, endQuarterDate, False, False) # call handleFx to update data

    # if handleFx fails...
    except Exception as e:

        print(f'Failed to update fx data. Returned with error: "{e}"\n') # print failure statement

    ##### metal commodities list #####

    try: # attempt to call handleMetal to neatly take care of agriculture functions...

        handle_metal(quandlKey, startQuarterDate, endQuarterDate, False, False) # call handleMetal to update data

    except Exception as e: # if handleMetal fails...

        print(f'Failed to update metal data. Returned with error: "{e}"\n') # print failure statement

    ##### cryptocurrency list #####

    # collect list of cryptocurrencies to analyze using ccxt

    ##### bond list #####

    # collect list of bonds to analyze using pandas datareader TODO RESEARCH FIXED RATE INVESTMENT INSTRUMENTS


########## RUN FILES AUTOMATICALLY ##########

def run_files_automatically(): # function to run files when on a machine

    ##### load API keys #####

    apiKeys = load_api_keys() # call loadAPIKeys to get all the necessary API keys
    alphaVantageKey = apiKeys.get('alpha_vantage', {}).get('api_key', None) # grab alpha vantage key
    quandlKey = apiKeys.get('quandl', {}).get('api_key', None) # grab quandl key
    ccxtKey = apiKeys.get('ccxt', {}).get('api_key', None) # grab ccxt key

    ########## create lists of data ##########

    # call getQuarterDates to determine start date at beginning of current quarter, end date current day
    startQuarterDate, endQuarterDate = get_quarter_dates()

    try: # attempt to call handleStocks to neatly take care of stock functions...

        # call handleStocks to update data
        handle_stocks(alphaVantageKey, startQuarterDate, endQuarterDate, False, False, True, False)

    except Exception as e: # if handleStocks fails...

        print(f'Failed to update stock data. Returned with error: "{e}"\n') # print failure statement

    ##### agricultural commodities list #####

    # attempt to call handleAgriculture to neatly take care of agriculture functions...
    try:

        # call handleAgriculture to update data
        handle_agriculture(quandlKey, startQuarterDate, endQuarterDate, False, False)

    except Exception as e: # if handleAgriculture fails...

        print(f'Failed to update agriculture data. Returned with error: "{e}"\n') # print failure statement

    ##### metal commodities list #####

    try: # attempt to call handleMetal to neatly take care of agriculture functions...

        handle_metal(quandlKey, startQuarterDate, endQuarterDate, False, False) # call handleMetal to update data

    except Exception as e: # if handleMetal fails...

        print(f'Failed to update metal data. Returned with error: "{e}"\n') # print failure statement

    ##### energy commodities list #####

    try: # attempt to call handleEnergy to neatly take care of energy functions...

        handle_energy(quandlKey, startQuarterDate, endQuarterDate, False, False) # call handleEnergy to update data

    except Exception as e: # if handleEnergy fails...

        print(f'Failed to update energy data. Returned with error: "{e}"\n') # print failure statement

    ##### fx contracts list #####

    try: # attempt to call handleFx to neatly take care of energy functions...

        handle_fx(quandlKey, startQuarterDate, endQuarterDate, False, False) # call handleFx to update data

    except Exception as e: # if handleFx fails...

        print(f'Failed to update fx data. Returned with error: "{e}"\n') # print failure statement

    ##### cryptocurrency list #####

    # collect list of cryptocurrencies to analyze using ccxt

    ##### bond list #####

    # collect list of bonds to analyze using pandas datareader TODO RESEARCH FIXED RATE INVESTMENT INSTRUMENTS


########## MANUAL MODE OPTION ##########

def manual_or_automatic(manualMode): # function to run files and route tensorflow based manualMode being true or false

    ##### set computational routes #####

    if manualMode == True: # if in development and want to run files manually...

        run_files_manually() # call runMFilesManually if developing

    else: # if file is running automatically on machine...

        run_files_automatically() # call runFilesAutomatically when running on machine





#####################################################
############### MANUAL MODE PARAMETER ###############
#####################################################


########## MANUAL MODE ##########

##### run files manually #####

manual_or_automatic(True) # if developing, and you want to manually run files, set to true