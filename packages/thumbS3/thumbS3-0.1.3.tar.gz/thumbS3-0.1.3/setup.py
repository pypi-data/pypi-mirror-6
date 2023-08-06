from distutils.core import setup

setup(
    name = 'thumbS3',
    py_modules = ['thumbs3'], 
    version = '0.1.3',
    description = 'Python module and command-line tool for creating thumbs on Amazon S3',
    author = 'Gianluca Tiepolo',
    author_email = 'tiepolo.gian@gmail.com',
    long_description=open('README.md').read(),
    url = 'https://github.com/tiepologian/thumbS3',  
    keywords = ['s3', 'thumbs', 'aws'], 
    classifiers = [],
    install_requires=[
        "argparse >= 1.2.1",
        "boto >= 2.2.2",
	"PIL >= 1.1.7",
	"Pillow >= 2.3.0",
	"requests >= 2.2.1",
    ],
)
