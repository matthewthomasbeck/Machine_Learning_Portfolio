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

##### data modeling libraries #####

from sklearn.preprocessing import MinMaxScaler # used to normalize data in between 0 and 1
import numpy as np # import numpy for data modeling
from collections import deque # used to store sequences in deque

##### machine learning libraries #####

from keras.models import Sequential # used to create an easy-to-make model with layers
from keras.layers import Dense, LSTM, Dropout # used to make different layer types to go with sequential


########## CREATE DEPENDENCIES ##########

##### machine learning constants #####

NUMBER_STEPS = 7 # set size of sequence to 1 week
BATCH_SIZE = 8 # set number of training instances to 8
EPOCHS = 80 # set number of data passes through machine learning algorithm to 80
scaler = MinMaxScaler() # set scaler for normalizing data





####################################################
############### TENSORFLOW FUNCTIONS ###############
####################################################


########## PREP DATA ##########

def prepare_financial_data(financialInstrumentData, days): # function to take data and make it tensorflow-friendly

    ##### create sequences #####

    # create a shallow copy of stock data with new values that point to old values
    prepFinancialInstrumentData = financialInstrumentData.copy()

    # create a new column for future data and shift back the closing price column by n days to allow for a target price
    prepFinancialInstrumentData['Future'] = prepFinancialInstrumentData['Close'].shift(-days)

    # convert close columns final days rows to a numpy array
    lastSequence = np.array(prepFinancialInstrumentData[['Close']].tail(days))

    # remove all days rows with missing values whilst returning the same dataframe
    prepFinancialInstrumentData.dropna(inplace=True)

    sequenceData = [] # declare an empty array to store sequences for model training

    sequences = deque(maxlen=NUMBER_STEPS) # create a deque of length n steps (1 week) to store sequences

    for entry, target in zip( # loop through all datapoints in close and future columns at the same type with zip

        # loop through the close and date columns in the stock data
        prepFinancialInstrumentData[['Close'] + ['Date']].values, prepFinancialInstrumentData['Future'].values
    ):

        sequences.append(entry) # add entry to the deque

        if len(sequences) == NUMBER_STEPS: # if the length of sequence is equal to number of steps...

            # add sequence and target value to sequence grouping for machine learning
            sequenceData.append([np.array(sequences), target])

    ##### create last sequence #####

    modifiedLastSequence = [] # create an empty list to store list of lists storing close column values

    for s in sequences: # loop through sequences to extract closing values

        # take the first value in the size 1 sequence (equivalent to s[0]) and store it in modified last sequence list
        modifiedLastSequence.append(s[:len(['Close'])])

    # combine modified list and original last sequence list of 32-bit floats
    lastSequence = list(modifiedLastSequence) + list(lastSequence)

    # convert last sequence into an array of 32-bit floats to lower numerical precision for faster computation
    lastSequence = np.array(lastSequence).astype(np.float32)

    ##### create lists of testing variables #####

    x, y = [], [] # create 2 lists x and y to store input variables and target variables

    for sequence, target in sequenceData: # loop through the length of sequence data to fill x and y lists

        x.append(sequence) # store the input variables in sequence data as x to use as a basis for the model

        y.append(target) # store the testing variables to use as testing material

    x = np.array(x) # convert sequence list into array for easier processing

    y = np.array(y) # convert target list into array for easier processing

    return prepFinancialInstrumentData, lastSequence, x, y # return prepared data to be inserted into tensorflow


########## CREATE MACHINE LEARNING MODEL ##########

def create_trained_model(trainX, trainY): # function to create a trained machine learning model

    ##### create model layers #####

    print("Creating model...\n") # print creating trained model update

    model = Sequential() # create an instance of sequential to add layers to

    # add long short term memory layer to sequential model of 60 neurons in the shape of len close column and
    # NUMBER_STEPS time steps and then return an output for each input to stack next LSTM layer
    model.add(LSTM(60, return_sequences=True, input_shape=(NUMBER_STEPS, len(['Close']))))

    # add a dropout layer to sequential model to prevent over fitting by setting 30% (0.3) of neuron input units to 0
    # during each update during training (prevents line from hugging literally every point of data, allowing for
    # generalization)
    model.add(Dropout(0.3))

    # add another LSTM layer to 120 neurons but do not return the full sequence of neurons
    model.add(LSTM(120, return_sequences=False))

    model.add(Dropout(0.3)) # add another dropout layer to turn off 30% of neurons for better linear generalization

    model.add(Dense(20)) # add a dense layer of 20 neurons to connect the neurons in the LSTM layers 1 and 3

    model.add(Dense(1)) # add a dense layer of 1 neuron to predict a continuous price value

    # compile sequential model with adam optimizer and mean squared error loss for regression
    model.compile(loss='mean_squared_error', optimizer='adam')

    # take input data and train model with BATCH_SIZE samples and EPOCHS times, trying to map input data trainX to
    # target data trainY with minimal progress reports
    model.fit(trainX, trainY, batch_size=BATCH_SIZE, epochs=EPOCHS, verbose=0)

    return model # return trained model
