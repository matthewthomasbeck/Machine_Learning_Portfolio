##################################################################################
# Copyright (c) 2025 Matthew Thomas Beck                                         #
#                                                                                #
# Licensed under the Creative Commons Attribution-NonCommercial 4.0              #
# International (CC BY-NC 4.0). Personal and educational use is permitted.       #
# Commercial use by companies or for-profit entities is prohibited.              #
##################################################################################





###################################################
############### IMPORT DEPENDENCIES ###############
###################################################


########## IMPORT DEPENDENCIES ##########

##### data collection libraries #####

import quandl # used to grab commodities data
from bs4 import BeautifulSoup # used to assign URL to a simple word instead of parsing a URL every time you need it
import requests # used to web scrape HTTP content for gold, silver, commodities prices
from selenium import webdriver # used to web parse dynamic content
from selenium.common.exceptions import WebDriverException # used incase webdriver fails to connect

##### data modeling libraries #####

import matplotlib.pyplot as plt # used for client graph visualization

##### miscellaneous libraries #####

import time # used with selenium for waiting





#####################################################
############### ENERGY DATA FUNCTIONS ###############
#####################################################


########## FIND VOLATILE CME COMMODITIES ##########

# function to find volatile agriculture financial instruments
def find_volatile_energy_commodities(quandlKey, startDate, endDate):

    with open( # open and read the txt file storing failed downloads

        './financialInstrument_data/agriculture_data/agriculture_data-clearing_tickers-CME.txt',
        'r'
    ) as CMEClearingTickersFile:

        # store failed downloads list into array
        CMEClearingTickers = [str(line.strip()) for line in CMEClearingTickersFile]

    quandl.ApiConfig.api_key = quandlKey # use quandl api key to collect commodities data

    print("Collecting data for each commodity...\n") # print finding volatile commodities progress statement

    for CMEClearingTicker in CMEClearingTickers: # loop through every commodity

        try: # EXPERIMENTING WITH COLLECTING DATA

            print(('CHRIS/CME_' + CMEClearingTicker))

            CMECommodityFile = (

                    './financialInstrument_data/agriculture_data/agriculture_data-' + CMEClearingTicker + '.csv'
            )

            #print(CMECommodityFile)

            CMECommodityData = quandl.get(('CHRIS/CME_' + CMEClearingTicker))

            CMECommodityData.to_csv(CMECommodityFile)

        except Exception as e:

            print(f'Failed to store agricultural data into respective csv. Returned with error: "{e}"\n')