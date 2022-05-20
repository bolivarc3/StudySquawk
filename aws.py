from app import BUCKET_NAME,s3
import os
import boto3
def upload(filespath,filename,filedata):
    #saving files to the s3 with a filepath and filename
        filedata.save(filename)
        s3.upload_file(
            Bucket = BUCKET_NAME,
            Filename=filename,
            Key = filespath +  "/" + filename
        )
        return "Upload Done ! "

def download_file(filespath, BUCKET_NAME):
    #filepath for the folder creation
    parentpath = os.getcwd()
    folderpath = str(parentpath) + "/static/" + str(filespath)
    print(folderpath)
    if not os.path.isdir(folderpath):
        os.makedirs(folderpath)
    
    #s3 information for downloads
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(BUCKET_NAME)

    #grabs the objects from the s3 bucket and downloads them
    objects = bucket.objects.filter(Prefix=filespath)
    for obj in objects:
        #from the objects, grab the paths and names
        path, filename = os.path.split(obj.key)
        #make the target path
        target = str(parentpath) + '/static/' + str(filespath) + "/" + str(filename)
        #download
        bucket.download_file(obj.key, target)