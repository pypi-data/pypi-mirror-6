# -*- coding: utf-8 -*-


import argparse
import yaml

from os import getcwd

from os.path import (
    abspath,
    dirname,
    exists,
    join,
    realpath,
    isabs
)

from s3deploy.s3 import init as init_s3
from s3deploy.core import (
    sync_static_site,
    overwrite_static_site
)

parser = argparse.ArgumentParser(
    description='Deploy to S3 with alacrity.'
)

parser.add_argument(
    'target_directory',
    help='The top-level directory containing your static site.'
)

parser.add_argument(
    '--config',
    help='The path to your config file.'
)

parser.add_argument(
    '--overwrite',
    help='Forcibly overwrite the target bucket. Defaults to false.',
    action='store_true'
)


def _scrub_path(path):
    if isabs(path):
        path = realpath(path)
    else:
        cwd = abspath(getcwd())
        path = realpath(join(cwd, path))
    return path


def _read_config(path):
    o = {}
    path = _scrub_path(path)
    if exists(path):
        with open(path, 'r') as f:
            o = yaml.load(f)
    return o


def main(*args, **kwargs):
    cli_args = vars(parser.parse_args())
    config = None

    if cli_args['config']:
        config = _read_config(cli_args['config'])
    else:
        cwd = getcwd()
        default_path = join(cwd, 's3deploy.config.yaml')
        if exists(default_path):
            config = _read_config(default_path)

    if not config:
        raise RuntimeError(
            'S3 Deploy cannot function without a config file :(')

    init_s3(config['aws_key'], config['aws_secret'])

    if cli_args['target_directory']:
        t_dir = _scrub_path(cli_args['target_directory'])
        b_name = config['bucket_name']

        if cli_args['overwrite']:
            overwrite_static_site(t_dir, b_name)
        else:
            sync_static_site(t_dir, b_name)
