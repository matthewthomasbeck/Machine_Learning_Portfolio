#!/bin/bash

##################################################################################
# Copyright (c) 2025 Matthew Thomas Beck                                         #
#                                                                                #
# Licensed under the Creative Commons Attribution-NonCommercial 4.0              #
# International (CC BY-NC 4.0). Personal and educational use is permitted.       #
# Commercial use by companies or for-profit entities is prohibited.              #
##################################################################################





###########################################
############### RUN PROCESS ###############
###########################################


########## SET UP LOG FILE ##########

echo -e "\nSetting up log file...\n"

##### set log file and clear it #####

# set log with path to txt
LOGFILE=""

# clear logfile
echo -e "Clearing log file at $LOGFILE...\n"
> "$LOGFILE"
echo -e "Log file cleared.\n"


########## RUN investmentGenie_main.py ##########

echo -e "Running investmentGenie_main.py...\n"

##### set virtual environment #####

# set virtual environment
echo -e "Activating virtual environment...\n"
source ""
echo -e "Virtual environment activated.\n"

##### verify virtual environment #####

# Log the Python interpreter path
echo -e "Python interpreter path:\n" >> "$LOGFILE"
which python3 >> "$LOGFILE"

# Log installed packages in the virtual environment
echo -e "Installed packages:\n" >> "$LOGFILE"
pip list >> "$LOGFILE"

##### run investmentGenie_main.py #####

# run investmentGenie_main.py with console output to log
echo -e "Running investmentGenie_main.py and logging output to $LOGFILE...\n"
/usr/bin/python3 "" >> "$LOGFILE" 2>&1
echo -e "Script execution completed. Check the log file for details.\n"