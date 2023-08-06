thumbS3
=======

Python module and command-line tool for creating thumbs on Amazon S3


### Installation

Install required packages:
```
sudo apt-get install python-dev libjpeg-dev libfreetype6 libfreetype6-dev zlib1g-dev
ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib
ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib
```
    
Install module:
```
sudo pip install thumbS3
```


### Module Usage:
```
from thumbS3.thumbs3 import ThumbS3

th = ThumbS3("my_aws_key", "my_aws_secret", "http://s3-eu-west-1.amazonaws.com/my_bucket_name", 150, 150)
th.setDestinationFolder("/thumbs")
th.setSuffix("_thumb")
th.setVerbose()

photos = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]

for name in photos:
    th.create(name)
  
# Resulting thumbs (150x150px)
# http://s3-eu-west-1.amazonaws.com/my_bucket_name/thumbs/photo1_thumb.jpg
# http://s3-eu-west-1.amazonaws.com/my_bucket_name/thumbs/photo2_thumb.jpg
# http://s3-eu-west-1.amazonaws.com/my_bucket_name/thumbs/photo3_thumb.jpg
```

### Command-line Usage:
```
usage: thumbs3.py [-h] [-k KEY] [-s SECRET] [-f FILENAME] [--url URL]
                  [--folder FOLDER] [--suffix SUFFIX] [--width WIDTH]
                  [--height HEIGHT] [-v]

thumbS3 command-line tool for creating thumbs on Amazon S3

Arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     Amazon AWS access key
  -s SECRET, --secret SECRET
                        Amazon AWS access key secret
  -f FILENAME, --filename FILENAME
                        Image filename
  --url URL             Amazon S3 bucket url
  --folder FOLDER       Thumbs destination folder
  --suffix SUFFIX       Thumbs filename suffix
  --width WIDTH         Thumb width
  --height HEIGHT       Thumb height
  -v, --verbose         increase output verbosity
```
