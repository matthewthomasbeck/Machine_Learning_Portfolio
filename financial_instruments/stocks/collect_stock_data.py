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


########### IMPORT DEPENDENCIES ###########

##### data collection libraries #####

import yfinance as yf # used to track stock values
import requests # used to web scrape HTTP content for gold, silver, commodities prices

##### data modeling libraries #####

import pandas as pd # used to read the downloaded csv

##### miscellaneous libraries #####

from tqdm import tqdm # used to track progress via progress bar





####################################################
############### STOCK DATA FUNCTIONS ###############
####################################################


########## RETRY FAILED DOWNLOADS ##########

def retry_failed_downloads(): # function to retry any failed ticker downloads

    ##### get failed downloads list #####

    with open( # open and read the txt file storing failed downloads

        './financialInstrument_data/stock_data/stock_data-failed_tickers.txt',
        'r'
    ) as failedStockDownloadsFile:

        # store failed downloads list into array
        prevFailedStockDownloads = [str(line.strip()) for line in failedStockDownloadsFile]

    ##### retry failed downloads #####

    successfulDownloads = [] # create a list of successful downloads to store successful downloads to

    for prevFailedStockDownload in tqdm(prevFailedStockDownloads): # loop through all failed downloads to retry download

        # download data with failed download ticker
        successfulDownload = yf.download(prevFailedStockDownload, progress=False)['Close']

        if not successfulDownload.empty: # if data returned by yfinance is not empty...

            print(f"\n{prevFailedStockDownload} successfully downloaded.") # print successful download statement

            successfulDownloads.append(prevFailedStockDownload) # update successful downloads list

    ##### update failed downloads #####

    # create a new array containing elements from the larger array not present in common set
    prevFailedStockDownloads = [x for x in prevFailedStockDownloads if x not in successfulDownloads]

    # print removed failed downloads success statement
    print(f"{len(successfulDownloads)} previously failed downloads now responsive.")

    print(successfulDownloads, "\n") # print successful downloads

    print("Updating failed downloads list...\n") # print volatile stocks list update statement

    # save volatile stocks list to volatile stocks file
    with open('./financialInstrument_data/stock_data/stock_data-failed_tickers.txt',
              'w') as failedStockDownloadsFile:

        for prevFailedDownload in prevFailedStockDownloads: # loop through every item in volatile stocks list

            if (prevFailedDownload != None): # if failed download is not NULL type...

                # save the name of the volatile stock to volatile stocks file
                failedStockDownloadsFile.write(f"{prevFailedDownload}\n")

    print("Successfully updated failed downloads list.\n") # print update success statement


########## UPDATE API LISTING DATA ##########

def update_stocks_listing_status(alphaVantageKey): # function to take new csv data from alpha vantage

    ##### get file from API #####

    # print progress statement to connect to Alpha Vantage API
    print(f"Finding data via API page connection with web link and Alpha Vantage API key...\n")

    stockPage = requests.get( # connect to alpha vantage api with key to retrieve page of useful data

        f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={alphaVantageKey}&datatype=csv',
        timeout=10
    )

    if stockPage.status_code == 200: # if page successfully loaded...

        # open csv of listing statuses of financial instruments
        with open('./financialInstrument_data/stock_data/listing_status.csv', 'wb') as listingStatusFile:

            listingStatusFile.write(stockPage.content) # store API data into file

        print("Successfully updated total stock listings.\n") # print API connection success statement

    else: # if page failed to load...

        # print API connection failure statement
        print(f'Failed to retrieve stockPage. Returned with status code: "{stockPage.status_code}"\n')


########## FIND ACTIVE STOCKS ##########

def find_active_stocks(alphaVantageKey): # function to find all stocks that are active within alpha vantage csv

    ##### find all active stocks #####

    update_stocks_listing_status(alphaVantageKey) # call updateStocksListingStatus to update listing information

    try: # attempt to loop through data for active stocks...

        # set stockData as a pandas dataframe
        stockData = pd.read_csv('./financialInstrument_data/stock_data/listing_status.csv')

        print("Attempting to find active stocks...\n") # print finding active stocks statement

        activeStocks = [] # empty array to hold all active stocks

        for i, stock in stockData.iterrows(): # loop through all items in stockData to find active stocks

            # if a ticker within the data set is active and is a stock...
            if stock['status'] == 'Active' and stock['assetType'] == 'Stock':

                activeStocks.append(stock['symbol']) # put the active stock into the activeStocks array

        ##### remove failed stock downloads #####

        prevFailedStockDownloads = [] # create empty list of previous failed downloads

        try: # attempt to get list of failed downloads...

            # open and read the txt file storing failed downloads
            with open('./financialInstrument_data/stock_data/stock_data-failed_tickers.txt',
                      'r') as failedStockDownloadsFile:

                # store failed downloads list into array
                prevFailedStockDownloads = [str(line.strip()) for line in failedStockDownloadsFile]

            # convert arrays to sets for efficient intersection
            prevFailedStockDownloads = set(activeStocks) & set(prevFailedStockDownloads)

            # create a new array containing elements from the larger array not present in common set
            activeStocks = [x for x in activeStocks if x not in prevFailedStockDownloads]

            # print removed failed downloads success statement
            print(f"Ignored {len(prevFailedStockDownloads)} previously failed downloads.\n")

        except Exception as e: # if unable to get failed downloads from list....

            print(f'Error reading failed downloads list: "{e}"\n') # print failure error with exception

        print(f"Successfully retrieved {len(activeStocks)} active stocks.\n") # print active stock success statement

        # return lists of active stocks and stocks that failed to download
        return activeStocks, prevFailedStockDownloads

    except Exception as e: # if unable to set json...

        print(f'Error parsing data: "{e}"\n') # print failure error with exception


########## FIND VOLATILE STOCKS ##########

# function to find volatile stocks (or any behavior you want) from the active stocks
def find_volatile_stocks(alphaVantageKey, startDate, endDate):

    ##### find active stocks #####

    # call findActiveStocks to get list of active stocks
    activeStocks, prevFailedStockDownloads = find_active_stocks(alphaVantageKey)

    if (activeStocks == 0 or prevFailedStockDownloads == 0): # if code failed...

        print("Error: findActiveStocks returned with 0.\n") # print error statement

        return 0 # return with 0 for failure

    ##### set variables #####

    volatileStocks = [] # create an empty array to store volatile stocks and their volumes
    failedStockDownloads = [] # create an empty array to store active stocks who've failed to download

    ##### find volatile stocks #####

    print("Attempting to find the most volatile active stocks...\n") # print find volatile stocks statement

    for i in tqdm(range(len(activeStocks))): # loop through activeStocks to find the most volatile stocks

        try: # attempt to download data with given active stock ticker...

            # download active stock's historical data from startDate to endDate
            activeStock = yf.download(activeStocks[i], progress=False)['Close']
            # start=startDate, end=endDate,

            # collect the earliest listing to see if stock is younger than startDate
            earliestListing = activeStock.index.min().strftime('%Y-%m-%d')

            if (earliestListing < startDate): # if maximum time active stock has been listed shorter than startDate...

                # restrict data to desired time frame
                activeStock = activeStock[(activeStock.index >= startDate) & (activeStock.index <= endDate)]

            else: # if maximum time active stock has been listed falls short of startDate...

                activeStock = activeStock[activeStock.index <= endDate] # restrict data to desired time frame

            if (activeStocks != None): # if data was successfully downloaded...

                # calculate volatility of active stock (standard deviation of daily returns)
                volatility = activeStock.pct_change().std() * (252 ** .05) * 100

                # if active stock is considered volatile and is at least 90 dollars...
                if (volatility > 5.5 and activeStock.iloc[-1] > 90):

                    volatileStocks.append(activeStocks[i]) # put the volatile stock into list of volatile stocks

                    # print volatility and name of volatile stock and keep newline
                    print(f"\r{activeStocks[i]} added: volatility = {volatility:.4f}%.")

            # print progress into console
            #print(f"\rVolatile stocks count: {len(volatileStocks)}.")
                  #f" Active stocks remaining: {len(activeStocks) - i}", end='', flush=True)

        except: # if unable to get active stocks data...

            failedStockDownloads.append(activeStocks[i]) # add failed download to failed downloads list

    ##### add volatile stocks to list #####

    print(f"Successfully calculated {len(volatileStocks)} volatile stocks.") # print volatile stocks success statement

    print(volatileStocks, "\n") # print all successful downloads

    if (len(volatileStocks) >= 1 and volatileStocks[0] != None): # if volatile stocks list not empty...

        print("Updating volatile stocks list...\n") # print volatile stocks list update statement

        # save volatile stocks list to volatile stocks file
        with open('./financialInstrument_data/stock_data/stock_data-volatile_tickers.txt', 'w') as volatileStocksList:

            for volatileStock in volatileStocks: # loop through every item in volatile stocks list

                volatileStocksList.write(f"{volatileStock}\n") # save name of volatile stock to volatile stocks file

        print("Successfully updated volatile stocks list.\n") # print update success statement

    ##### add failed downloads to list #####

    if (len(failedStockDownloads) >= 1 and failedStockDownloads[0] != None): # if failed downloads list not empty...

        # if null value error persists, remove null values
        failedStockDownloads = [failedDownload for failedDownload in failedStockDownloads if failedDownload is not None]

        # print volatile stocks failed downloads statement
        print(f"Unsuccessfully calculated {len(failedStockDownloads)} volatile stocks.")

        print(failedStockDownloads, "\n") # print all failed downloads

        print("Updating failed downloads list...\n") # print update failed downloads statement

        # add all current failed downloads list to previous failed downloads list
        failedStockDownloads = list(prevFailedStockDownloads) + failedStockDownloads

        with open( # save failed downloads list to failed stock downloads file

            './financialInstrument_data/stock_data/stock_data-failed_tickers.txt',
            'w'
        ) as failedStockDownloadsFile:

            for activeStock in failedStockDownloads: # loop through every item in failed downloads list

                # save the name of the failed download to failed stock downloads file
                failedStockDownloadsFile.write(f"{activeStock}\n")

        print("Successfully updated failed downloads list.\n") # print update success statement

    else: # if length of failed downloads list is empty...

        print("No new failed downloads to update.\n") # print empty failed downloads statement

    print("Completed finding new volatile stocks.\n") # print final completion statement