# -*- coding: utf-8 -*-


from os import walk

from os.path import (
    join
)

from s3deploy.s3 import (
    upload_files,
    setup_bucket
)


def parse_target_dir(path):
    file_dict = {}
    for root, dirs, files in walk(path):
        for f in files:
            p = join(root, f)
            k = p.replace(path, '')[1:]
            file_dict[p] = k
    return file_dict


def sync_static_site(path, bucket_name):
    file_dict = parse_target_dir(path)
    upload_files(file_dict, bucket_name)


def overwrite_static_site(path, bucket_name):
    file_dict = parse_target_dir(path)
    setup_bucket(bucket_name)
    upload_files(file_dict, bucket_name)
