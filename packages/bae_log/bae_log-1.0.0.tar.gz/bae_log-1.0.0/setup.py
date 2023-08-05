try:
    from setuptools import *
except ImportError:
    from distutils.core import *

VERSION = "1.0.0"

setup(
    name = "bae_log",
    version = VERSION,
    author = "Zhang Guanxing",
    author_email = "zhangguanxing01@baidu.com",
    description = ("BAE Log SDK for V3.0"),
    keywords = "bae log sdk",
    url = "http://developer.baidu.com",
    packages= find_packages(), 
    install_requires = ["thrift>=0.9.0"],
    zip_safe = False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2 :: Only",
    ],
)
