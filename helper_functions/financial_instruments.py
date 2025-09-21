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

##### data collection functions #####

from financial_instruments.stocks.model_stock_data import create_stocks_model

# used to handle stock data
from financial_instruments.stocks.collect_stock_data import find_volatile_stocks
from financial_instruments.stocks.collect_stock_data import retry_failed_downloads

# used to handle agriculture data
from financial_instruments.agriculture.scrape_agriculture_names_cme import \
    find_cme_agriculture_names
from financial_instruments.agriculture.collect_agriculture_data import \
    find_volatile_agriculture_commodities

# used to handle energy data
from financial_instruments.energy.scrape_energy_names_cme import find_cme_energy_names
from financial_instruments.energy.collect_energy_data import \
    find_volatile_energy_commodities

# used to handle fx data
from financial_instruments.fx.scrape_fx_names_cme import find_cme_fx_names
from financial_instruments.fx.collect_fx_data import find_volatile_fx_contracts

# used to handle metal data
from financial_instruments.metals.scrape_metals_names_cme import find_cme_metal_names
from financial_instruments.metals.collect_metals_data import find_volatile_metals_commodities

from helper_functions.create_metrics import create_metrics # used to create data

##### miscellaneous libraries #####

import time # used to track runtime

##### create global time frame #####

timeFrames = [7, 30, 90, 365, 'max'] # time frame for plot creation





#####################################################
############### COLLECT DATA FUNCTIONS ##############
#####################################################


########## STOCKS ##########

def handle_stocks( # function to neatly handle stock values

    alphaVantageKey,
    startDate,
    endDate,
    updateVolatileStocks,
    machineLearnStocks,
    createNewPlot,
    updateFailedDownloads
):

    ##### preset dependencies #####

    # declare custom tickers list
    customTickers = ['NVDA', 'META', 'GOOG', 'AMZN', 'MSFT', 'TSLA']
    #customTickers = ['SQ']
    start = time.time() # start loop timer

    ##### find volatile stocks #####

    if (updateVolatileStocks == True): # if user wants to update list of volatile stocks...

        try: # try to update volatile stocks list...

            # call findVolatileStocks to update list of volatile stocks
            find_volatile_stocks(alphaVantageKey, startDate, endDate)

        except Exception as e: # if unable to update volatile stocks list...

            print(f'Error updating volatile stocks list: "{e}"') # print failure error with exception

    ##### model data with tensorflow #####

    if (machineLearnStocks == True): # if user wants to machine learn stocks...

        try: # try to machine learn...

            create_stocks_model(startDate, endDate, customTickers) # call createStocksModel to machine learn

        except Exception as e: # if unable to machine learn list...

            print(f'Error machine learning stocks: "{e}"\n') # print failure error with exception

    ##### plot data with plotly #####

    if (createNewPlot == True): # if user wants to plot new data...

        try: # attempt to plot new data...

            create_metrics('Stocks', timeFrames) # call createGraph to plot new data with 'Stocks' type over timeFrame

            print(f"Successfully plotted new stocks data.") # print success statement

        except Exception as e: # if unable to plot new data...

            print(f'Error plotting new data: "{e}"') # print failure error with exception

    ##### update failed stock downloads #####

    if (updateFailedDownloads == True): # if user wants to update list of failed downloads...

        try: # try to update volatile stocks list...

            retry_failed_downloads() # call retryFailedDownloads to update list of failed downloads

        except Exception as e: # if unable to update volatile stocks list...

            print(f'Error updating failed downloads list: "{e}"') # print failure error with exception

    ##### find elapsed time to loop #####

    runTimeMinutes, runTimeSeconds = divmod((time.time() - start), 60) # find elapsed time to loop

    # print volatile stocks completion statement
    print(f"\nAnalyzed stock data in {int(runTimeMinutes)} minutes and {runTimeSeconds:.2f} seconds.\n")


########## AGRICULTURE ##########

def handle_agriculture( # function to neatly handle agriculture values

        quandlKey,
        startQuarterDate,
        endQuarterDate,
        updateAgricultureCommodityNames,
        updateVolatileAgricultureCommodities
):

    ##### preset dependencies #####

    start = time.time() # start loop timer

    ##### update agricultural commodity names #####

    if (updateAgricultureCommodityNames == True): # if user wants to update list of agricultural commodity names...

        try: # try to update agricultural commodity names list...

            # call findCMEAgricultureNames to update list of agricultural commodity names
            find_cme_agriculture_names()

        except Exception as e: # if unable to update agricultural commodity names list...

            print(f'Error updating agricultural commodity names: "{e}"') # print failure error with exception

    ##### find volatile agricultural futures #####

    if (updateVolatileAgricultureCommodities == True): # if user wants to update list of agricultural commodity names...

        try: # try to find volatile agricultural commodity futures...

            # call findVolatileAgriculture to find volatile agricultural futures
            find_volatile_agriculture_commodities(quandlKey, startQuarterDate, endQuarterDate)

        except Exception as e: # if unable to find volatile agricultural futures

            print(f'Error finding volatile agricultural futures: "{e}"') # print failure error with exception

    ##### find elapsed time to loop #####

    runTimeMinutes, runTimeSeconds = divmod((time.time() - start), 60) # find elapsed time to loop

    # print volatile agricultural commodities completion statement
    print(f"Analyzed agriculture data in {int(runTimeMinutes)} minutes and {runTimeSeconds:.2f} seconds.\n")


########## ENERGY ##########

def handle_energy( # function to neatly handle energy values

        quandlKey,
        startQuarterDate,
        endQuarterDate,
        updateEnergyCommodityNames,
        updateVolatileEnergyCommodities
):

    ##### preset dependencies #####

    start = time.time() # start loop timer

    ##### update energy commodity names #####

    if (updateEnergyCommodityNames == True): # if user wants to update list of energy commodity names...

        try: # try to update energy commodity names list...

            find_cme_energy_names() # call findCMEEnergyNames to update list of energy commodity names

        except Exception as e: # if unable to update energy commodity names list...

            print(f'Error updating energy commodity names: "{e}"') # print failure error with exception

    ##### find volatile energy futures #####

    if (updateVolatileEnergyCommodities == True): # if user wants to update list of energy commodity names...

        try: # try to find volatile energy commodity futures...

            # call findVolatileEnergy to find volatile energy futures
            find_volatile_energy_commodities(quandlKey, startQuarterDate, endQuarterDate)

        except Exception as e: # if unable to find volatile energy futures

            print(f'Error finding volatile energy futures: "{e}"') # print failure error with exception

    ##### find elapsed time to loop #####

    runTimeMinutes, runTimeSeconds = divmod((time.time() - start), 60) # find elapsed time to loop

    # print volatile energy commodities completion statement
    print(f"Analyzed energy data in {int(runTimeMinutes)} minutes and {runTimeSeconds:.2f} seconds.\n")


########## FOREIGN EXCHANGE ##########

def handle_fx( # function to neatly handle fx values

        quandlKey,
        startQuarterDate,
        endQuarterDate,
        updateFxContractNames,
        updateVolatileFxContracts

):

    ##### preset dependencies #####

    start = time.time() # start loop timer

    ##### update fx contract names #####

    if (updateFxContractNames == True): # if user wants to update list of fx contract names...

        try: # try to update fx contract names list...

            find_cme_fx_names() # call findCMEEnergyNames to update list of fx contract names

        except Exception as e: # if unable to update fx contract names list...

            print(f'Error updating fx contract names: "{e}"') # print failure error with exception

    ##### find volatile fx contracts #####

    if (updateVolatileFxContracts == True): # if user wants to update list of fx contract names...

        try: # try to find volatile fx contract futures...

            # call findVolatileEnergy to find volatile fx contracts
            find_volatile_fx_contracts(quandlKey, startQuarterDate, endQuarterDate)

        except Exception as e: # if unable to find volatile fx contracts

            print(f'Error finding volatile fx contracts: "{e}"') # print failure error with exception

    ##### find elapsed time to loop #####

    runTimeMinutes, runTimeSeconds = divmod((time.time() - start), 60) # find elapsed time to loop

    # print volatile fx contracts completion statement
    print(f"Analyzed fx data in {int(runTimeMinutes)} minutes and {runTimeSeconds:.2f} seconds.\n")


########## METAL ##########

def handle_metal( # function to neatly handle metal values

        quandlKey,
        startQuarterDate,
        endQuarterDate,
        updateMetalContractNames,
        updateVolatileMetalContracts

):

    ##### preset dependencies #####

    start = time.time() # start loop timer

    ##### update metal commodity names #####

    if (updateMetalContractNames == True): # if user wants to update list of metal commodity names...

        try: # try to update metal commodity names list...

            find_cme_metal_names() # call findCMEEnergyNames to update list of metal commodity names

        except Exception as e: # if unable to update metal commodity names list...

            print(f'Error updating metal commodity names: "{e}"') # print failure error with exception

    ##### find volatile metal commodities #####

    if (updateVolatileMetalContracts == True): # if user wants to update list of metal commodity names...

        try: # try to find volatile metal commodity futures...

            # call findVolatileEnergy to find volatile metal commodities
            find_volatile_metals_commodities(quandlKey, startQuarterDate, endQuarterDate)

        except Exception as e: # if unable to find volatile metal commodities

            print(f'Error finding volatile metal commodities: "{e}"') # print failure error with exception

    ##### find elapsed time to loop #####

    runTimeMinutes, runTimeSeconds = divmod((time.time() - start), 60) # find elapsed time to loop

    # print volatile metal commodities completion statement
    print(f"Analyzed metal data in {int(runTimeMinutes)} minutes and {runTimeSeconds:.2f} seconds.\n")