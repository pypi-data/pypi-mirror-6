#-*-coding: utf-8-*-

from setuptools import setup,find_packages


config = {
    "name": "pyweixin2",
    "keywords" : ('weixin' , 'sdk'),
    "install_requires" : ['poster>=0.8','XML2Dict>=0.2'],
    "description": "Weixin Software Development Kit(Python)",
    "author": "Freedom(WangChao)",
    "url": "https://github.com/lockmind/weixin-python-sdk",
    "download_url": "https://github.com/lockmind/weixin-python-sdk/archive/master.zip",
    "author_email": "wangchao0126@gmail.com",
    "version": "0.2",
    "license": "MIT",
    "packages" : find_packages(),
    "platforms" : 'any',
    "zip_safe": False
}

setup(**config)
