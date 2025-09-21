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

# import upload to codecommit function
from helper_functions.upload_to_aws import upload_to_code_commit
from helper_functions.upload_to_aws import upload_to_s3 # import upload to s3 function

##### import libraries needed to create and export plotly graph #####

import plotly.graph_objs as go # import graph objects for plotly
import plotly.offline as offline # import offline mode for plotly
import pandas as pd # import pandas for data manipulation


########## CREATE DEPENDENCIES ##########

##### s3 variables #####

s3BucketName = 'cdn.matthewthomasbeck.com'  # set s3 bucket name



##################################################
############### CREATE PLOTLY PLOT ###############
##################################################


########## FIND DATA SOURCE ##########

##### define where to draw data #####

def locate_data(graphType): # define function to locate data source

    dataPaths = { # dictionary to map graph type with data source

        'Stocks': './financialInstrument_data/stock_data/stock_data-closing_predictions-custom_tickers.csv',
        'Agriculture': './financialInstrument_data/agriculture_data/agriculture_data-closing_predictions.csv',
        'Energy': './financialInstrument_data/energy_data/energy_data-closing_predictions.csv',
        'Foreign Exchange': './financialInstrument_data/fx_data/fx_data-closing_predictions.csv',
        'Metal': './financialInstrument_data/metal_data/metal_data-closing_predictions.csv',
        'Crypto': './financialInstrument_data/crypto_data/crypto_data-closing_predictions.csv',
        'Bonds': './financialInstrument_data/bond_data/bond_data-closing_predictions.csv'
    }

    if graphType in dataPaths: # if graph type is valid...

        return dataPaths[graphType] # return data source

    else: # if graph type is invalid...

        print('ERROR: Invalid graph type.\n') # log as invalid

        return 0 # return nothing

def find_time_frame_title(timeFrame): # define function to set time frame title

    timeFrameTitle = { # dictionary to map time frame with title

        7: 'One Week', # set time frame as week
        30: 'One Month', # set time frame as month
        90: 'Three Months', # set time frame as three months
        365: 'Year To Day', # set time frame as year to day
        'max': 'All Time' # set time frame as all time
    }

    if timeFrame in timeFrameTitle: # if time frame is valid...

        return timeFrameTitle[timeFrame] # return correct title

    else: # if time frame is invalid...

        print('ERROR: Invalid time frame\n') # log as invalid

        return 0 # return nothing


########## CALCULATE PERCENT ACCURACY ##########

def calculate_percent_accuracy(actualClosing, predictedClosing): # define function to calculate percent accuracy

    ##### set variables #####

    actualClosing = pd.Series(actualClosing) # set actual closing data as pandas series
    predictedClosing = pd.Series(predictedClosing) # set predicted closing data as pandas series

    actualClosingAverage = actualClosing.mean() # find the average value of the actual closing data

    # find total variance of the dependent variable, in this case, the actual closing data
    tss = ((actualClosing - actualClosingAverage) ** 2).sum()

    # find the discrepancies between the actual and predicted closing values to find prediction accuracy
    rss = ((actualClosing - predictedClosing) ** 2).sum()

    ##### calculate r-squared for percent accuracy #####

    # find coefficient of determination r squared to find out how often the algorithm is correct
    rSquared = 1 - (rss / tss)

    percentAccuracy = round((rSquared * 100), 2) # multiply r squared by 100 for percentage figure to 2 decimal points

    return percentAccuracy # return percentage accuracy


########## CREATE PLOTLY PLOT ##########

def create_graph(graphType, timeFrame): # define function to create and export plotly graph

    ##### set variables #####

    # set color palette for max 12 traces
    colorPalette = ['#fcf6bd', '#f1f6c6', '#e6f5ce', '#dbf5d6', '#d0f4de', '#c9edea', '#c3e7f4', '#bde0fe', '#c6d8fb', '#ced0f8', '#d6c8f5', '#dec0f1']
    financialInstrumentPath = locate_data(graphType) # locate data source and set path

    # set output directory and file name for graph
    outputPathGraphs = './assets/graphs/' + graphType.lower() + 'Plot-' + str(timeFrame) + '.html'

    # set codecommit object name for graph
    codeCommitGraphObject = 'assets/machine_learning_portfolio/graphs/' + graphType.lower() + 'Plot-' + str(timeFrame) + '.html'
    codeCommitRepository = 'MTB_Website' # set codecommit repository name
    codeCommitBranch = 'main' # set codecommit branch

    ##### find time frame #####

    if timeFrame == 'max': # if time frame is max...

        financialInstrumentData = pd.read_csv(financialInstrumentPath) # read data source and set all data
        unalteredFinancialInstrumentData = financialInstrumentData[1:].copy() # create copy of original data source

    else: # if time frame is not max...

        financialInstrumentData = pd.read_csv(financialInstrumentPath) # read data source and set data
        unalteredFinancialInstrumentData = financialInstrumentData[1:].copy() # create copy of original data source
        financialInstrumentData = financialInstrumentData.tail(timeFrame) # set data to time frame

    ##### set variables cont. #####

    fig = go.Figure() # create figure
    totalRows = len(financialInstrumentData) # get total rows in data source
    selectedRows = 4 # number of prediction indexes to display
    lastTradingDayIndex = financialInstrumentData['Date'].iloc[(totalRows - selectedRows)] # get last trading day index for vertical line
    predictionsBeginningIndex = totalRows - selectedRows # get index for beginning of predictions line
    i = 0 # dummy looping variable columns
    j = 0 # dummy looping variable for colors
    movementOverTime = []  # create empty list for growth over time
    names = []  # create empty list for names
    firstPredictions = [] # create empty list for first predictions
    secondPredictions = [] # create empty list for second predictions
    thirdPredictions = [] # create empty list for third predictions
    movementProjected = [] # create empty list for projected growth
    colors = []  # create empty list for colors
    percentAccuracy = []
    actualClosing = []  # record actual closing data
    predictedClosing = []  # record predicted closing data


    ##### create graph #####

    for column in financialInstrumentData.columns[1:]: # loop through each column besides the date

        ##### set variables #####

        color = colorPalette[j] # set color for both lines
        tickerName = column.split()[0] # set ticker name for hover

        #### set up predicted data column ####

        if 'Predicted' in column: # if data is predictions...

            ##### set variables #####

            # set closing data to predicted closing data
            closeData = financialInstrumentData[column][predictionsBeginningIndex:]
            dates = financialInstrumentData['Date'][predictionsBeginningIndex:] # set dates to predicted dates

            # set closing data to hidden closing data
            closeDataHidden = financialInstrumentData[column][:predictionsBeginningIndex]
            datesHidden = financialInstrumentData['Date'][:predictionsBeginningIndex] # set dates to hidden dates
            predictionCoordsX = dates[-3:] # set last three x-axis points
            predictionCoordsY = closeData[-3:] # set last three y-axis points
            predictionCoordsLastX = dates.iloc[-1] # set last x-axis point
            predictionCoordsLastY = closeData.iloc[-1] # set last y-axis point

            ##### gather data for json #####

            if (timeFrame == 7): # if beginning of data collection...

                # collect predicted closing data
                predictedClosing = unalteredFinancialInstrumentData[column]

                # calculate percent accuracy
                percentAccuracy.append(calculate_percent_accuracy(actualClosing, predictedClosing))
                firstPredictions.append(round(predictionCoordsY.iloc[0], 2)) # add first prediction to list
                secondPredictions.append(round(predictionCoordsY.iloc[1], 2)) # add second prediction to list
                thirdPredictions.append(round(predictionCoordsY.iloc[2], 2)) # add third prediction to list
                earliestEntry = closeData.iloc[0] # get earliest entry

                # add projected percent growth from latest actual entry to latest predicted entry
                movementProjected.append(round((((predictionCoordsLastY - earliestEntry) / earliestEntry) * 100), 2))

            ##### create prediction trace #####

            fig.add_trace(go.Scatter( # create predicted trace

                x=dates, # set x-axis to date
                y=closeData, # set y-axis to predicted closing price
                mode='lines', # set mode to lines
                line=dict( # set line properties

                    dash='dot', # set line style to dotted
                    color=color, # set line color
                ),
                name=tickerName, # set name to ticker name
                hovertemplate='<br><b>%{x|%b %d}</b><br>%{y:$,.2f}', # set hover template
                hoverlabel=dict( # set hover label properties

                    font=dict( # set font properties

                        family='monospace', # set font family
                        color='#212529' # set font color
                    ),
                    align='left', # set alignment to left
                    bordercolor='rgba(0,0,0,0)' # set border color to transparent
                ),
                showlegend=False # hide legend
            ))

            ##### create hidden prediction trace #####

            fig.add_trace(go.Scatter( # create predicted trace

                x=datesHidden, # set x-axis to date
                y=closeDataHidden, # set y-axis to predicted closing price
                mode='lines', # set mode to lines
                line=dict( # set line properties

                    dash='dot', # set line style to dotted
                    color=color, # set line color
                ),
                name=tickerName, # set name to ticker name
                hovertemplate='<br><b>%{x|%b %d}</b><br>%{y:$,.2f}', # set hover template
                hoverlabel=dict( # set hover label properties

                    font=dict( # set font properties

                        family='monospace', # set font family
                        color='#212529' # set font color
                    ),
                    align='left', # set alignment to left
                    bordercolor='rgba(0,0,0,0)' # set border color to transparent
                ),
                showlegend=False # hide legend
            ))

            ##### create prediction markers #####

            fig.add_trace(go.Scatter( # create predicted markers

                x=predictionCoordsX, # set x-axis to last three dates
                y=predictionCoordsY, # set y-axis to last three predicted closing prices
                mode='markers+text', # set mode to markers and text
                marker=dict(size=8, color=color, symbol='circle'), # set marker properties
                name=tickerName, # set name to ticker name
                hovertemplate='<br><b>%{x|%b %d}</b><br>%{y:$,.2f}', # set hover template
                hoverlabel=dict( # set hover label properties

                    font=dict( # set font properties

                        family='monospace', # set font family
                        color='#212529' # set font color
                    ),
                    align='left', # set alignment to left
                    bordercolor='rgba(0,0,0,0)' # set border color to transparent
                ),
                showlegend=False # hide legend
            ))

            ##### create permanent label #####

            fig.add_annotation( # create permanent label for last prediction

                x=predictionCoordsLastX, # set x-axis to last date
                y=predictionCoordsLastY, # set y-axis to last predicted closing price
                xshift=10, # set x-shift to 10 to move label to the right
                yshift=0, # set y-shift to 0
                text=f"{tickerName}", # set text to ticker name
                showarrow=False, # hide arrow
                font=dict( # set font properties

                    color=color, # set font color to line color
                    family='monospace', # set font family
                    size=8 # set font size
                ),
                align='left', # set alignment to far left
                xanchor='left' # set x-anchor to far left
            )

            j = j + 1 # increment to change color for next ticker

        ##### set up actual data column #####

        else: # if data is actual...

            #### set variables ####

            # set closing data to actual closing data
            closeData = financialInstrumentData[column].head(predictionsBeginningIndex + 1)
            dates = financialInstrumentData['Date'].head(predictionsBeginningIndex + 1) # set dates to actual dates
            earliestEntry = closeData.iloc[0] # get earliest entry for growth calculation
            latestEntry = closeData.iloc[-1] # get latest entry for growth calculation
            actualCoordX = dates[-1:] # set latest x-coordinate
            actualCoordY = closeData[-1:] # set latest y-coordinate

            ##### gather data for json #####

            if (timeFrame == 7): # if beginning of data collection...

                # collect actual closing data
                actualClosing = unalteredFinancialInstrumentData[column]

                names.append(tickerName) # set name for financial instrument
                colors.append(color) # set color for financial instrument

            if earliestEntry is None or pd.isna(earliestEntry): # if earliest entry is empty...

                earliestEntry = closeData.loc[closeData.first_valid_index()] # get first valid index

                # calculate growth over time
                movementOverTime.append(round((((latestEntry - earliestEntry) / earliestEntry) * 100), 2))

            else: # if earliest entry is not empty...

                # calculate growth over time
                movementOverTime.append(round((((latestEntry - earliestEntry) / earliestEntry) * 100), 2))

            ##### create actual trace #####

            fig.add_trace(go.Scatter( # create actual trace

                x=dates, # set x-axis to date
                y=closeData, # set y-axis to closing price
                mode='lines', # set mode to lines
                name=tickerName, # set name to ticker name
                line=dict( # set line properties

                    color=color # set line color
                ),
                hovertemplate='<br><b>%{x|%b %d}</b><br>%{y:$,.2f}', # set hover template
                hoverlabel=dict( # set hover label properties

                    font=dict( # set font properties

                        family='monospace', # set font family
                        color='#212529' # set font color
                    ),
                    align='left', # set alignment to left
                    bordercolor='rgba(0,0,0,0)' # set border color to transparent
                ),
                showlegend=False # hide legend
            ))

            ##### create actual marker #####

            fig.add_trace(go.Scatter( # create predicted markers

                x=actualCoordX, # set x-axis to last trading date
                y=actualCoordY, # set y-axis to last closing price
                mode='markers+text', # set mode to markers and text
                marker=dict(size=8, color=color, symbol='circle'),  # set marker properties
                name=tickerName, # set name to ticker name
                hovertemplate='<br><b>%{x|%b %d}</b><br>%{y:$,.2f}', # set hover template
                hoverlabel=dict( # set hover label properties

                    font=dict( # set font properties

                        family='monospace', # set font family
                        color='#212529' # set font color
                    ),
                    align='left', # set alignment to left
                    bordercolor='rgba(0,0,0,0)' # set border color to transparent
                ),
                showlegend=False # hide legend
            ))

        ##### increment column index #####

        i = i + 1 # increment column index

    ##### set up graph look #####

    fig.update_layout( # control what the plot looks like

        dragmode=False, # disable graph manipulation
        xaxis=dict( # handle x-axis

            showline=True, # show x-axis line
            linewidth=1, # set thin line width
            linecolor='white', # make line color white
            gridcolor='#212529' # x-axis grid color
        ),
        yaxis=dict( # handle y-axis

            showline=True, # show y-axis line
            linewidth=1, # set thin line width
            linecolor='white', # make line color white
            gridcolor='#212529', # y-axis grid color
            tickprefix="$", # give y axis dollar sign values
            zeroline=False, # get rid of zero line
            zerolinewidth=0 # get rid of zero line
        ),
        plot_bgcolor='#212529', # plot background color
        paper_bgcolor='#212529', # paper background color
        margin=dict( # remove margins for as much space as possible

            l=0, # set left margin to 0
            r=0, # set right margin to 0
            t=25, # set top margin for last trading day bar label and line label
            b=0 # set bottom margin to 0
        ),
        font=dict( # set font

            size=10, # set font size
            family='monospace', # font family
            color='white' # font color
        ),
        shapes=[dict( # add vertical line for trading day
                type='line', # set line
                xref='x', # x
                yref='paper', # y
                x0=lastTradingDayIndex, # set x position
                y0=0, # set y position
                x1=lastTradingDayIndex, # set x position
                y1=1, # set y position
                line=dict( # style line

                    color='white', # set as white
                    width=1, # set width
                    dash='dash' # set line style
                )
            )
        ]
    )

    ##### add annotation to trading day line #####

    fig.add_annotation( # add annotation to trading day line

        x=lastTradingDayIndex, # set x position as last trading day
        y=1, # set y coordinate at the top of the graph
        text="Last Trading Day", # set annotation text
        font=dict( # set font properties

            color='white', # set font color to white
            family='monospace', # set font family
            size=8 # set font size
        ),
        showarrow=False, # hide arrow
        yanchor="bottom", # set y anchor to bottom
        yref='paper' # set y reference to paper
    )

    ##### export plot file #####

    offline.plot(  # save plot as HTML file

        fig, # set figure
        filename=outputPathGraphs, # set file path
        auto_open=False, # do not open plot in browser
        config={ # set configuration

            'displayModeBar': False # hide mode bar
        }
    )

    ##### upload graph to codecommit repository #####

    # upload data to codecommit
    upload_to_code_commit(outputPathGraphs, codeCommitRepository, codeCommitBranch, codeCommitGraphObject)

    ##### create dataframe to export #####

    if (timeFrame == 7): # if beginning of data collection...

        financialInstrumentsTable = pd.DataFrame({ # create table for financial instruments to export as json

            'Name': names, # set names
            'Color': colors, # set colors
            'Prediction Accuracy': percentAccuracy, # set percent accuracy
            'Prediction 1': firstPredictions, # set first predictions
            'Prediction 2': secondPredictions, # set second predictions
            'Prediction 3': thirdPredictions, # set third predictions
            'Projected Movement': movementProjected, # set projected growth
            f'Movement {find_time_frame_title(timeFrame)}': movementOverTime # set growth over time
        })

        #print(financialInstrumentsTable)

        return financialInstrumentsTable # return a full dataframe

    else: # if data collection has already begun...

        return movementOverTime # return movement over time


########## CREATE ALL PLOTLY PLOTS WITH DATA ##########

def create_metrics(graphType, timeFrames): # create graphs for all time frames

    ##### set variables #####

    outputPathData = './assets/data/' + graphType.lower() + 'Data.json' # set output directory and file name for data
    s3DataObject = 'assets/machine_learning_portfolio/data/' + graphType.lower() + 'Data.json' # set s3 object name
    financialInstrumentsTable = 0 # initialize variable

    ##### create graphs for all time frames #####

    for timeFrame in timeFrames: # for each time frame...

        if (timeFrame == 7): # if beginning of data collection...

            financialInstrumentsTable = create_graph(graphType, timeFrame) # create graph for time frame and return table

        else: # if data collection has already begun...

            movementOverTime = create_graph(graphType, timeFrame) # create graph for time frame and return total movement

            # add movement over time column to table
            financialInstrumentsTable[f'Movement {find_time_frame_title(timeFrame)}'] = movementOverTime

    ##### export json file #####

    financialInstrumentsJson = financialInstrumentsTable.to_json(orient='records') # convert table to json for export

    with open(outputPathData, 'w') as financialInstrumentsFile: # open json file to write data

        financialInstrumentsFile.write(financialInstrumentsJson) # write json data to file

    ##### upload json data to s3 bucket #####

    upload_to_s3(outputPathData, s3BucketName, s3DataObject) # upload data to s3 bucket