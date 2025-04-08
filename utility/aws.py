import boto3, os, uuid

s3_client = boto3.client('s3') #, aws_access_key_id = config.AWS_ACCESS_KEY_ID, aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY, region_name = config.AWS_REGION)
s3_resource = boto3.resource('s3') #, aws_access_key_id = config.AWS_ACCESS_KEY_ID, aws_secret_access_key = config.AWS_SECRET_ACCESS_KEY, region_name = config.AWS_REGION)

def find_bucket_key(s3_path):
    """
    This is a helper function that given an s3 path such that the path is of
    the form: bucket/key
    It will return the bucket and the key represented by the s3 path
    """
    s3_components = s3_path.split('/')
    bucket = s3_components[0]
    s3_key = ""
    if len(s3_components) > 1:
        s3_key = '/'.join(s3_components[1:])
    return bucket, s3_key

def split_s3_bucket_key(s3_path):
    """Split s3 path into bucket and key prefix.
    This will also handle the s3:// prefix.
    :return: Tuple of ('bucketname', 'keyname')
    """
    if s3_path.startswith('s3://'):
        s3_path = s3_path[5:]
    return find_bucket_key(s3_path)

def download_from_s3(s3_uri):
    bucket, filename = split_s3_bucket_key(s3_uri)
    unique_folder = str(uuid.uuid4())[0:8]
    os.makedirs(os.path.join(os.getcwd(), "/tmp", unique_folder), exist_ok=True)
    
    filepath = os.path.join(os.getcwd(), "/tmp", unique_folder, filename)
    s3_resource.Bucket(bucket).download_file(filename, filepath)
    return filepath