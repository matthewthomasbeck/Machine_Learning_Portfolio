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


########### IMPORT DEPENDENCIES ##########

##### name collection libraries #####

from bs4 import BeautifulSoup # used to assign URL to a simple word instead of parsing a URL every time you need it
import requests # used to web scrape HTTP content for gold, silver, commodities prices
from selenium import webdriver # used to web parse dynamic content
from selenium.common.exceptions import WebDriverException # used incase webdriver fails to connect

##### miscellaneous libraries #####

import time # used with selenium for waiting





###########################################################
############### AGRICULTURAL NAME FUNCTIONS ###############
###########################################################


########## FIND CME SUBPAGES ##########

def find_cme_subpages(): # function to find subpages on CME website

    ##### connect to CME exchange #####

    print("Attempting to connect to CME exchange webpage...\n") # print connecting to page progress statement

    agent = ( # create a fake user agent for CME

        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/85.0.4183.102 Safari/537.36"
    )

    CMEWebpage = requests.get( # connect to CME exchange with fake user agent

        'https://www.cmegroup.com/markets/agriculture.html#products',
        timeout=10,
        headers={'user-agent': agent}
    )

    if CMEWebpage.status_code == 200: # if successfully connected to CME...

        print("Successfully connected to CME exchange webpage.\n") # print connection success statement

        ##### find subpages #####

        CMEWebpageParser = BeautifulSoup(CMEWebpage.content, 'html.parser') # create webpage as object from html markup

        print("Searching for commodity subpages...\n") # print searching for commodities progress statement

        anchorTags = CMEWebpageParser.find_all( # collect a list of all desired commodity type subpages

            'a',
            class_='chevron-right'
        )

        CMESubpages = [] # declare empty list to store commodity subpages for further scraping

        for anchorTag in anchorTags: # loop through every anchor tag found

            CMESubpage = anchorTag.get('href') # save link in href as a subpage

            # if subpage link starts with desired path...
            if CMESubpage.startswith(f'/trading/agricultural/') or CMESubpage.startswith(f'/markets/agriculture/'):

                CMESubpages.append('https://www.cmegroup.com' + CMESubpage) # add link to list of subpages

        CMESubpages = list(set(CMESubpages)) # remove any duplicate subpages

        # print subpage success statement
        print(f"Successfully found {len(CMESubpages)} commodity subpages: {CMESubpages}.\n")

        return CMESubpages # return list of subpages

    else: # if connection unsuccessful...

        # print status code failure statement
        print(f'Failed to connect to CME webpage. Returned with status code: "{CMEWebpage.status_code}"\n')


########## FIND CME COMMODITY PAGES ##########

def find_cme_commodity_pages(): # function to get a list of commodity page links

    ##### set variables #####

    CMESubpages = find_cme_subpages() # call findCMESubpages to get a list of pages to sort through
    CMECommodityPages = [] # declare an empty list to store individual commodity pages
    driver = webdriver.Chrome() # create a new webdriver instance

    ##### search through subpages #####

    print("Searching for commodity pages...\n") # print commodities in subpages progress statement

    for CMESubpage in CMESubpages: # loop through every subpage found

        try: # attempt to open the dynamic webpage with webdriver...

            driver.get(CMESubpage) # open subpage

            time.sleep(5) # wait 5 seconds for javascript content to load

            CMESubpageSource = driver.page_source # store page source after dynamic content has loaded

            CMESubpageParser = BeautifulSoup(CMESubpageSource, 'html.parser') # create subpage source as an object

            ##### find commodity pages #####

            listElements = CMESubpageParser.find_all( # find elements that contain anchor tags for products

                ['td', 'th'],
                class_='cmeTableLeft'
            )

            if not listElements: # if a page is empty...

                CMECommodityPages.append(CMESubpage) # add link to list of commodity pages (used for lumber exception)

            else: # if a page contains elements...

                for listElement in listElements: # loop through every listing element

                    anchorTag = listElement.find( # find all anchor tags within elements that may contain a link

                        'a',
                    )

                    if anchorTag: # if anchor tag containing a link found...

                        CMECommodityPages.append( # save link to commodity pages list with specs

                            'https://www.cmegroup.com' + anchorTag.get('href')
                        )

        except WebDriverException as e: # if page fails to open...

            print(f'Failed to connect to CME subpage. Returned with error: "{e}"\n') # print webdriver failed error

    driver.quit() # close the webdriver

    CMECommodityPages = list(set(CMECommodityPages)) # remove any duplicate pages

    # print commodity page success statement
    print(f'Successfully found {len(CMECommodityPages)} commodity pages: "{CMECommodityPages}."\n')

    return CMECommodityPages # return list of commodity pages


########## FIND CME COMMODITY SPECS ##########

def find_cme_commodity_specs(): # function to get a list of all agricultural commodity specs

    ##### set variables #####

    CMECommodityPages = find_cme_commodity_pages() # call findCMECommodityPages to get list of commodity pages
    CMEGlobexTickers = [] # create empty list to store commodity tickers
    CMECommoditySpecs = [] # create empty list to store commodity specs
    driver = webdriver.Chrome() # create a new webdriver instance

    ##### search through commodity pages #####

    print("Searching for globex tickers and commodity specs...\n") # print commodities names progress statement

    for CMECommodityPage in CMECommodityPages: # loop through every commodity page name

        try: # attempt to open the dynamic webpage with webdriver...

            driver.get(CMECommodityPage) # open commodity page

            time.sleep(5) # wait 5 seconds for javascript content to load

            CMECommodityPage = driver.page_source # store page source after dynamic content has loaded

            ##### find commodity globex tickers #####

            CMECommodityPageParser = BeautifulSoup(CMECommodityPage, 'html.parser') # create page source as an object

            span = CMECommodityPageParser.find( # find span element that holds globex ticker name

                'span',
                class_='globex'
            )

            if span: # if span items found...

                CMEGlobexTickers.append(span.text.strip()) # save found link to list of globex tickers

            ##### find commodity specs #####

            CMECommodityPageParser = BeautifulSoup(CMECommodityPage, 'html.parser') # create page source as an object

            specsAttributes = { # set attributes to look for in specs button

                'class': 'menu-item',
                'data-key': 'contractSpecs',
                'role': 'button',
                'tabindex': '0'
            }

            # find anchor element that holds next link
            anchorTag = CMECommodityPageParser.find('div', attrs=specsAttributes).find('a')

            CMECommoditySpecs.append(anchorTag.get('href')) # save found link to list of spec pages

        except WebDriverException as e: # if page fails to open...

            print(f'Failed to connect to CME subpage. Returned with error: "{e}"\n') # print webdriver failed error

    driver.quit() # close the webdriver

    ##### save globex tickers #####

    CMEGlobexTickers = list(set(CMEGlobexTickers)) # remove any duplicate globex tickers

    # print globex tickers success statement
    print(f"Successfully found {len(CMEGlobexTickers)} globex tickers: {CMEGlobexTickers}.\n")

    with open( # save globex tickers to globex tickers file

            './financialInstrument_data/agriculture_data/agriculture_data-current_globex_tickers-CME.txt',
            'w'
    ) as CMEGlobexTickersFile:

        for CMEGlobexTicker in CMEGlobexTickers: # loop through every item in globex tickers list

            CMEGlobexTickersFile.write(f"{CMEGlobexTicker}\n") # save the globex ticker to the globex tickers file

    ##### save commodity specs #####

    CMECommoditySpecs = list(set(CMECommoditySpecs)) # remove any duplicate specs

    # print commodity specs success statement
    print(f"Successfully found {len(CMECommoditySpecs)} commodity specs: {CMECommoditySpecs}.\n")

    return CMECommoditySpecs # return list of commodity specs


########## FIND CME COMMODITY NAMES ##########

def find_cme_agriculture_names(): # function to get a list of all agricultural commodity names

    ##### set variables #####

    CMECommoditySpecs = find_cme_commodity_specs() # call findCMECommoditySpecs to get list of commodity specs
    CMECommodityNames = [] # create empty list to store commodity names
    driver = webdriver.Chrome() # create a new webdriver instance

    ##### search through commodity pages #####

    print("Searching for commodity names...\n") # print commodities names progress statement

    for CMECommoditySpec in CMECommoditySpecs: # loop through every commodity page name

        try: # attempt to open the dynamic webpage with webdriver...

            driver.get(CMECommoditySpec) # open commodity page

            time.sleep(5) # wait 5 seconds for javascript content to load

            CMECommoditySpec = driver.page_source # store page source after dynamic content has loaded

            CMECommoditySpecParser = BeautifulSoup(CMECommoditySpec, 'html.parser') # create spec source as an object

            ##### find clearing tickers #####

            divs = CMECommoditySpecParser.find_all( # find anchor element that holds next link

                'div',
                class_='item-container'
            )

            i = 0 # begin div index

            for div in divs: # loop through each div

                spans = div.find_all('span') # find spans within div

                if spans: # if spans are found within a div...

                    j = 0 # begin span sub-index

                    if (i == 2): # if current index is 3rd div...

                        for span in spans: # loop through each span

                            if (j == 1): # if current sub-index is 2nd span...

                                CMECommodityNames.append(span.text.strip()) # add text within to commodity names list

                            j = j + 1 # increment span sub-index

                    i = i + 1 # increment div index

        except WebDriverException as e: # if page fails to open...

            print(f'Failed to connect to CME subpage. Returned with error: "{e}"\n') # print webdriver failed error

    driver.quit() # close the webdriver

    CMECommodityNames = list(set(CMECommodityNames)) # remove any duplicate names

    # print commodity page success statement
    print(f"Successfully found {len(CMECommodityNames)} commodity names: {CMECommodityNames}.\n")

    with open( # save commodity names to commodity names file

        './financialInstrument_data/agriculture_data/agriculture_data-clearing_tickers-CME.txt',
        'w'
    ) as CMECommodityNamesFile:

        for CMECommodityName in CMECommodityNames: # loop through every item in commodity names list

            CMECommodityNamesFile.write(f"{CMECommodityName}\n") # save name of commodity to commodity names file