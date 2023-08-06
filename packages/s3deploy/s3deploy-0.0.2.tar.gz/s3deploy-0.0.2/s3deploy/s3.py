# -*- coding: utf-8 -*-


from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import S3CreateError

_connection = None


def init(aws_key, aws_secret):
    global _connection
    if not _connection:
        _connection = S3Connection(aws_key, aws_secret)


def create_bucket(bucket_name):
    try:
        bucket = _connection.create_bucket()
    except S3CreateError:
        raise RuntimeError('Choose another bucket name...')
    return bucket


def erase_bucket(bucket):
    bucket.delete_keys(bucket.list())


def setup_bucket(bucket_name):
    bucket = _connection.get_bucket(bucket_name)
    if not bucket:
        bucket = create_bucket(bucket_name)
    else:
        erase_bucket(bucket)
    bucket.configure_website(suffix='index.html')


def upload_files(path_dict, bucket_name):
    bucket = _connection.get_bucket(bucket_name)
    for path, filename in path_dict.iteritems():
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_filename(path)
    bucket.make_public(recursive=True)
