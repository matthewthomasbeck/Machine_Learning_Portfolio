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

##### s3 uploading #####

import boto3 # import boto3 to upload to s3
from botocore.exceptions import NoCredentialsError # import NoCredentialsError to handle errors

##### sagemaker invocation #####

from sagemaker.tensorflow import TensorFlow # import TensorFlow to use sagemaker's tensorflow capabilities


########## CREATE DEPENDENCIES ##########

##### machine learning constants #####

NUMBER_STEPS = 7 # set size of sequence to 1 week
BATCH_SIZE = 8 # set number of training instances to 8
EPOCHS = 80 # set number of data passes through machine learning algorithm to 80





#############################################
############### UPLOAD TO AWS ###############
#############################################


########## UPLOAD TO S3 ##########

def upload_to_s3(outputPathData, s3BucketName, s3ObjectName=None): # function to upload file to s3

    ##### set variables #####

    if s3ObjectName is None: # if object name not provided...

        s3ObjectName = outputPathData # set object name to file name

    s3_client = boto3.client( # create s3 client

        's3', # set service name
        aws_access_key_id = '', # set access key id
        aws_secret_access_key = '', # set secret access key
        region_name = 'us-east-2' # set region name
    )

    ##### upload file to s3 #####

    try: # attempt to upload file...

        s3_client.upload_file(outputPathData, s3BucketName, s3ObjectName) # upload file to s3

        print(f"File {outputPathData} uploaded to {s3BucketName}/{s3ObjectName}.\n") # print success message

    except FileNotFoundError: # if file not found...

        print(f"File {outputPathData} not found.\n") # print error message

    except NoCredentialsError: # if credentials not found...

        print("Credentials not available.\n") # print error message


########## DOWNLOAD FROM S3 ##########

def download_from_s3(bucketName, s3Key, localPath): # function to download file from s3

    s3_client = boto3.client( # create s3 client

        's3', # set service name
        aws_access_key_id = '', # set access key id
        aws_secret_access_key = '', # set secret access key
        region_name = 'us-east-2' # set region name
    )

    s3_client.download_file(bucketName, s3Key, localPath) # download file from s3

    print(f"File {s3Key} downloaded from {bucketName} to {localPath}.\n") # print success message



########## UPLOAD TO AMPLIFY ##########

def upload_to_code_commit(outputPathGraphs, codeCommitRepository, codeCommitBranch, codeCommitGraphObject):

    codeCommitClient = boto3.client( # create codecommit client

        'codecommit', # set service name
        aws_access_key_id = '',
        aws_secret_access_key = '',
        region_name = 'us-east-2' # set region name
    )

    branch_info = codeCommitClient.get_branch( # get branch info

        repositoryName=codeCommitRepository, # set repository name
        branchName=codeCommitBranch # set branch name
    )

    lastCommitID = branch_info['branch']['commitId'] # get last commit id

    with open(outputPathGraphs, 'r') as file: # open file

        file_content = file.read() # read file

    try: # attempt to upload to repo...

        put_file_response = codeCommitClient.put_file( # put file in codecommit

            repositoryName=codeCommitRepository, # set repository name
            branchName=codeCommitBranch, # set branch name
            fileContent=file_content.encode('utf-8'), # set file content
            filePath=codeCommitGraphObject, # set file path
            fileMode='NORMAL', # set file mode
            parentCommitId=lastCommitID, # set parent commit id
            commitMessage='machine_learning_portfolio graph update' # set commit message
        )

        # print success message
        print(f"File {put_file_response} successfully uploaded to {codeCommitRepository}:{codeCommitBranch}.\n")

    except Exception: # if error occurs...

        print(f"Error uploading file to {codeCommitRepository}:{codeCommitBranch}: {Exception}\n") # print error message


########## INVOKE SAGEMAKER ##########

# function to invoke sagemaker process
def invoke_sagemaker(trainXS3DataObject, trainYS3DataObject, s3BucketName, modelPath):

    ##### set variables #####
    sagemakerTrainingScript = ''
    sagemakerTrainingURI = ''
    executionRole = ''
    trainXS3DataPath = f's3://{s3BucketName}/{trainXS3DataObject}'
    trainYS3DataPath = f's3://{s3BucketName}/{trainYS3DataObject}'
    modelS3Path = f's3://{s3BucketName}/{modelPath}'
    modelLocalPath = ''

    ##### create estimator #####

    try: # attempt to create sagemaker process...

        try: # try to make estimator

            estimator = TensorFlow(

                entry_point=sagemakerTrainingScript,
                role=executionRole,
                instance_count=1,
                instance_type='ml.m5.large',
                framework_version='2.3.0',
                py_version='py36',
                hyperparameters={

                    'epochs': EPOCHS,
                    'batch-size': BATCH_SIZE
                },
                image_uri=sagemakerTrainingURI,
                input_mode='File',
                #output_path=modelS3Path,
                output_path=None,
                base_job_name='machine-learning-portfolio-training'
            )

            ##### train model to completion #####

            trainingData = {

                'train-x': trainXS3DataPath,
                'train-y': trainYS3DataPath
            }

            estimator.fit(inputs=trainingData, wait=True)  # fit model to training data and wait until completed

        except Exception as e:

            print(f"Error creating estimator: {e}\n")

        print("Model training complete.\n") # print success message

        ##### download model from s3 bucket #####

        download_from_s3(s3BucketName, modelPath, modelLocalPath) # download model from s3 bucket

        return modelLocalPath # Return model object

    except Exception as e:

        print(f"Error training model: {e}\n") # print error message