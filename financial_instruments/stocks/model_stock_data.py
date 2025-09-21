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

##### aws uploading #####

from helper_functions.upload_to_aws import upload_to_s3 # import upload to s3 function
from helper_functions.upload_to_aws import invoke_sagemaker # import invoke sagemaker function

##### machine learning functions #####

# used to prepare data for machine learning
from helper_functions.create_tensorflow_model import prepare_financial_data

# used to create recursive neural network LSTM
#from helper_functions.tensorflow_functions.tensorflowFunctions_createModel import createTrainedModel

##### data collection libraries #####

import pandas as pd # used to create final dataframe
import yfinance as yf # used to collect stock data

##### data modeling libraries #####

from sklearn.preprocessing import MinMaxScaler # used to normalize data in between 0 and 1
import numpy as np # import numpy for data modeling

##### miscellaneous libraries #####

from datetime import datetime # used to convert str to date format

##### machine learning libraries #####

import tensorflow as tf # used to use h5 from path


########## CREATE DEPENDENCIES ##########

##### machine learning constants #####

NUMBER_STEPS = 7 # set size of sequence to 1 week

FUTURE_STEPS = [1, 2, 3] # number of days in week to be examined

scaler = MinMaxScaler() # set scaler for normalizing data

##### miscellaneous constants #####

dateFormat = '%Y-%m-%d' # set date format to be month day year

##### s3 variables #####

s3BucketName = 'machine-learning-portfolio' # set s3 bucket name 'machine-learning-portfolio-fractal-labs'





####################################################
############### STOCK DATA FUNCTIONS ###############
####################################################


########## ORGANIZE AND MODEL DATA ##########

def create_stocks_model(startDate, endDate, customTickers): # function to collect data from current quarter

    ##### calculate date interval #####

    print("Calculating date interval...\n") # print finding interval statement

    # find the total amount of days to be displayed
    intervalLength = (datetime.strptime(endDate, dateFormat) - datetime.strptime(startDate, dateFormat)).days

    print(f"Interval length: {intervalLength}.\n") # print desired time interval

    ##### get names of all stocks #####

    print("Retrieving ticker names...\n") # print fetching ticker names statement

    if customTickers: # if custom tickers list is not empty...

        tickerNames = customTickers # use custom ticker names as list to draw from

        # use custom tickers csv for output file
        predictionOutput = './financialInstrument_data/stock_data/stock_data-closing_predictions-custom_tickers.csv'

    else: # if custom tickers list is empty

        # open and read the txt file storing volatile stocks
        with open('./financialInstrument_data/stock_data/stock_data-volatile_tickers.txt', 'r') as volatileStocksList:

            tickerNames = [str(line.strip()) for line in volatileStocksList] # store volatile stocks list into array

        # use regular csv for output file
        predictionOutput = './financialInstrument_data/stock_data/stock_data-closing_predictions.csv'

    print("Successfully retrieved ticker names.\n") # print ticker name success statement

    ##### set variables #####

    stocksActual = pd.DataFrame() # create a dataframe to record all findings for all stocks
    stocksPredicted = 0 # initialize predicted dataframe
    i = 0 # initialize counter to 0 for number of stocks

    ##### collect data for all stocks #####

    print("Using ticker names to model price movement data...\n") # print fetching data statement

    for ticker in tickerNames: # loop through every ticker name

        ##### set variables #####

        # get daily historical data of closing prices for a share
        stockData = yf.download(ticker, end=endDate, interval='1d', progress=False)

        # remove unnecessary columns which neural network will not use
        stockData = stockData.drop(['Open', 'High', 'Low', 'Adj Close', 'Volume'], axis=1)
        stockData['Date'] = stockData.index # index data to its date(s)

        # normalize data for tensorflow
        stockData['Close'] = scaler.fit_transform(np.expand_dims(stockData['Close'].values, axis=1))
        model, trainX, trainY = 0, 0, 0 # initialize variables to be used in model
        stockPredictions = [] # create an empty list to store price predictions

        ##### create predictions for a stock #####

        for step in FUTURE_STEPS: # create a price prediction for stocks up to 3 days

            ##### set variables #####

            # call prepareStockData to get necessary sequences, filtered data, target data, etc.
            prepStockData, lastSequence, trainX, trainY = prepare_financial_data(stockData, step)
            trainX = trainX[:, :, :len(['Close'])].astype(np.float32) # set to 32-int float for processing
            stocksTrainXDataPath = './financialInstrument_data/stock_data/stock_data-trainX_data.npy' # set path
            stocksTrainYDataPath = './financialInstrument_data/stock_data/stock_data-trainY_data.npy' # set path
            stocksTrainXS3DataObject = 'financialInstrument_data/stock_data/stock_data-trainX_data.npy' # set object
            stocksTrainYS3DataObject = 'financialInstrument_data/stock_data/stock_data-trainY_data.npy' # set object
            stocksModelPath = 'financialInstrument_data/stock_data/stock_data-model.h5' # set path

            # extract the last NUMBER_STEPS (7) from the last sequence array to consider only the most recent
            # observations
            lastSequence = lastSequence[-NUMBER_STEPS:]

            # ensure the last sequence array has the correct shape before using it for predictions
            lastSequence = np.expand_dims(lastSequence, axis=0)

            ##### convert and send data to s3 for sagemaker #####

            print("Attempting to upload data to s3...\n")  # print uploading data statement

            np.save(stocksTrainXDataPath, trainX) # save training data to path as numpy binary
            np.save(stocksTrainYDataPath, trainY) # save target data to path as numpy binary
            upload_to_s3(stocksTrainXDataPath, s3BucketName, stocksTrainXS3DataObject) # upload training data to s3
            upload_to_s3(stocksTrainYDataPath, s3BucketName, stocksTrainYS3DataObject) # upload target data to s3

            print("Successfully uploaded data to s3.\n")  # print upload success statement

            ##### invoke sagemaker to train model #####

            print("Attempting to create model...\n") # print creating model statement

            # call createTrainedModel with testing and target variables to train model TODO
            #model = createTrainedModel(trainX, trainY) # original, home made method
            #model = invokeSageMaker(stocksTrainXS3DataObject, stocksTrainYS3DataObject, s3BucketName, stocksModelPath)
            model = tf.keras.models.load_model(

                invoke_sagemaker(stocksTrainXS3DataObject, stocksTrainYS3DataObject, s3BucketName, stocksModelPath)
            )

            print("Successfully created model.\n") # print model success statement

            prediction = model.predict(lastSequence) # use last sequence to make predictions

            # reverse normalization of the first element from the batch dimension in order to create accurate prices
            predictedPrice = scaler.inverse_transform(prediction)[0][0]

            stockPredictions.append(predictedPrice) # round the predicted price to 2 decimal places

        ##### print predictions #####

        # if there are predictions present and predictions list is not empty...
        if bool(stockPredictions) == True and len(stockPredictions) > 0:

            # add data from predictions to predictions list with dollar sign TODO remove for price
            #stockPredictionsList = [str(d) + '%' for d in stockPredictions]
            stockPredictionsList = ['$' + str(d) for d in stockPredictions]

            threePredictions = ', '.join(stockPredictionsList) # add comma after every prediction

            i = i + 1 # increment number of stocks predicted

            # print stock predictions statement
            print(f'\n{i}\{len(tickerNames)}: {ticker} predictions for the upcoming 3 days: {threePredictions}.\n')

        ##### create dataframe to save #####

        # create a shell copy of stock data with new variables that point to old variables
        stockDataCopy = stockData.copy()

        # create a prediction with trained input variables
        predictY = model.predict(trainX)

        # transform prediction values by reversing normalization and then remove any unnecessary single dimensions
        # previously necessary for inverse_transform()
        predictYTransformed = np.squeeze(scaler.inverse_transform(predictY))

        # find first sequence by expanding the dimension of first 6 elements in trainY for inverse_transform() and then
        # reverse normalization
        firstSequence = scaler.inverse_transform(np.expand_dims(trainY[:6], axis=1))

        # find first sequence by expanding the dimension of first 6 elements in trainY for inverse_transform() and then
        # reverse normalization
        lastSequence = scaler.inverse_transform(np.expand_dims(trainY[-3:], axis=1))

        # add transformed y predictions to the end of first sequence
        predictYTransformed = np.append(firstSequence, predictYTransformed)

        # add last sequence to the end of transformed y predictions
        predictYTransformed = np.append(predictYTransformed, lastSequence)

        # add transformed y predictions to the copied dataframe
        stockDataCopy['Predicted Close'] = predictYTransformed

        # reverse normalization for close column
        stockDataCopy['Close'] = scaler.inverse_transform(np.expand_dims(stockData['Close'], axis=1))

        stocksActual[ticker + ' Close'] = stockDataCopy['Close'] # fill dataframe with closing prices

        # fill dataframe with predicted prices
        stocksActual[ticker + ' Predicted Close'] = stockDataCopy['Predicted Close']

        ##### record predictions #####

        if (i == 1): # if first stock prediction...

            latestBusinessDay = stocksActual.index[-1] # get the latest business day

            # get the next 3 business days
            nextThreeBusinessDays = pd.bdate_range(start=latestBusinessDay + pd.Timedelta(days=1), periods=3)

            stocksPredicted = pd.DataFrame(index=nextThreeBusinessDays) # create a dataframe with next 3 business days

            stocksPredicted.index.name = 'Date' # set index name to 'Date'

        # fill close column with 3 predictions
        stocksPredicted[ticker + ' Close'] = stockPredictions

        # fill prediction column with 3 predictions
        stocksPredicted[ticker + ' Predicted Close'] = stockPredictions

    print("Finalized all stock predictions.\n") # print prediction completion statement

    ##### prepare and save data to csv #####

    # combine the actual and prediction dataframes
    stocksActualAndPredictions = pd.concat([stocksActual, stocksPredicted])

    stocksActualAndPredictions.to_csv(predictionOutput, header=True) # save actual data and predictions to csv file

    ##### upload json data to s3 bucket #####

    #uploadToS3(outputPathData, s3BucketName, s3DataObject) # upload data to s3 bucket