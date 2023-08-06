# -*- coding: utf-8 -*-


from setuptools import (
    setup,
    find_packages
)

setup(
    name="s3deploy",
    version="0.0.1",
    description='The quickest way to deploy a static site to S3',
    long_description=open('README.md').read(),
    keywords='',
    url='http://github.com/petermelias/s3-deploy',
    author='Peter M. Elias',
    author_email='petermelias@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'boto',
        'pyyaml'
    ],
    extras_require={
        'test': [
            'coveralls',
            'nose'
        ]
    },
    entry_points={
        'console_scripts': [
            's3deploy = s3deploy:main'
        ]
    },
    test_suite='nose.collector',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
