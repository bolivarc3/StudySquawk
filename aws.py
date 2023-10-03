from app import BUCKET_NAME,s3
import os
import boto3
import uuid
import errno

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

def assert_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def download_folder(bucket, path, zip_folder_number,base_folder):
    base_folder = base_folder.split("/")
    base_folder.pop()
    parentpath = os.getcwd()
    root_path = str(parentpath) + "/static/zip/"
    folderpath = root_path + zip_folder_number + "/"
    if not os.path.isdir(folderpath):
        os.makedirs(folderpath)
    target = folderpath
        # Handle missing / at end of prefix
    if not path.endswith('/'):
        path += '/'
    client = boto3.client('s3',aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),)
    paginator = client.get_paginator('list_objects_v2')

    for result in paginator.paginate(Bucket=bucket, Prefix=path):
        # Download each file individually
        for key in result['Contents']:
            # Calculate relative path
            rel_path_origin_folder = key['Key'].split("/")
            rel_path_origin_folder = rel_path_origin_folder[len(base_folder)-1]
            print(rel_path_origin_folder)
            rel_path = rel_path_origin_folder + "/" + key['Key'][len(path):]
            print(rel_path)
            # Skip paths ending in /
            if not key['Key'].endswith('/'):
                local_file_path = os.path.join(target, rel_path)
                # print("key:" + str(key['Key']))
                # print("target:" + str(local_file_path))
                # Make sure directories exist
                local_file_dir = os.path.dirname(local_file_path)
                print("\n")
                assert_dir_exists(local_file_dir)
                client.download_file(bucket, key['Key'], local_file_path)


def delete_aws_files(objectroute,name,object_type):
    key = "resources" + objectroute + "/"+ name
    if object_type == "folder":
        key = key + "/"
        s3 = boto3.resource('s3',aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),)
        bucket = s3.Bucket(BUCKET_NAME)
        bucket.objects.filter(Prefix=key).delete()
    else:
        client = boto3.client('s3',aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),)
        client.delete_object(Bucket=BUCKET_NAME, Key=key)

def delete_aws_files_post(objectroute,name,object_type):
    key = objectroute
    print(key)
    if object_type == "folder":
        key = key + "/"
        s3 = boto3.resource('s3',aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),)
        bucket = s3.Bucket(BUCKET_NAME)
        bucket.objects.filter(Prefix=key).delete()
    else:
        client = boto3.client('s3',aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),)
        client.delete_object(Bucket=BUCKET_NAME, Key=key)