import codecs
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# 定义版本和描述信息
VERSION = "1.0.0"
DESCRIPTION = "A tool for comparing two Pandas DataFrame objects"
LONG_DESCRIPTION = long_description

setup(
    name="dfcompy",
    version=VERSION,
    author="GuangJun Liang",
    author_email="gaungjun_l@icloud.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas', 'tabulate'],
    keywords=["python", "pandas", "dataframe", "compare", "diff", "data analysis"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ]
)
