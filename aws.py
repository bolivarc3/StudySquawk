from app import BUCKET_NAME,s3
import os
import boto3
import uuid

def upload(filespath,filename,filedata):
    #saving files to the s3 with a filepath and filename
    parentpath = os.getcwd()
    folderpath = str(parentpath) + "/static/" + str(filespath)
    if not os.path.isdir(folderpath):
        os.makedirs(folderpath)
    tofilepath = folderpath + "/" + str(filename)
    filedata.save(tofilepath)
    s3.upload_file(
        Bucket = BUCKET_NAME,
        Filename=tofilepath,
        Key = filespath +  "/" + filename
    )
    return "Upload Done ! "


def download_file(filespath, filename, BUCKET_NAME, zip_folder_number):
    #filepath for the folder creation
    parentpath = os.getcwd()
    root_path = str(parentpath) + "/static/zip/"
    folderpath = root_path + zip_folder_number + "/"
    target= root_path + zip_folder_number + "/" +str(filename)
    print(folderpath)
    print(filespath)
    if not os.path.isdir(folderpath):
        os.makedirs(folderpath)
    
    s3 = boto3.client('s3',
    aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
    )

    s3.download_file(
        Bucket=BUCKET_NAME,
        Key=filespath,
        Filename=target
    )