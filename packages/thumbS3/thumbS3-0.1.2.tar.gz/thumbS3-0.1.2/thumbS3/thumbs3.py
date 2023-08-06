#!/usr/bin/python

#
# Link:    https://github.com/tiepologian/thumbS3
# Author:  Gianluca Tiepolo
# Version: 0.1.2
# Description: Python module and command-line tool for creating thumbs on Amazon S3
#

from PIL import Image
from StringIO import StringIO
from optparse import OptionParser
from os.path import isfile,basename
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import requests, os.path, cStringIO, sys, argparse

class ThumbS3:
    def __init__(self, user, passw, url, width, height):
        try:
            self.conn = S3Connection(user, passw)
    	    self.bucket = self.conn.get_bucket(os.path.basename(url))
        except:
            print "Error connecting to Amazon S3"
            sys.exit(1)
        self.size = (width, height)
        self.url = url
        self.dest = ""
	self.suffix = "_thumb"
        self.verbose = False
        return

    def setDestinationFolder(self, path):
        self.dest = path

    def setSuffix(self, s):
        self.suffix = s

    def setVerbose(self):
        self.verbose = True

    def create(self, filename):
        try:
            response = requests.get(self.url+"/"+filename)
	    im = Image.open(StringIO(response.content))
            im.thumbnail(self.size)
            out_im = cStringIO.StringIO()
            im.save(out_im, 'JPEG')
            name = "%s/%s%s.jpg" % (self.dest, os.path.splitext(os.path.basename(filename))[0], self.suffix)
            if self.verbose:
                print "CREATING THUMB%s: %s" % (self.size, self.url+name)
            k = Key(self.bucket)
            k.key = name
            k.set_contents_from_string(out_im.getvalue(), headers={"Content-Type": "image/jpeg"})
            k.set_acl('public-read')
        except:
            print "ERROR: Unable to download source image"
            sys.exit(1)


def main():
    # Program entry point: check arguments, download image, create thumb and upload it to S3
    parser = argparse.ArgumentParser(description='thumbS3 command-line tool for creating thumbs on Amazon S3')
    parser.add_argument("-k", "--key", help="Amazon AWS access key")
    parser.add_argument("-s", "--secret", help="Amazon AWS access key secret")
    parser.add_argument("-f", "--filename", help="Image filename")
    parser.add_argument("--url", help="Amazon S3 bucket url")
    parser.add_argument("--folder", help="Thumbs destination folder", default="")
    parser.add_argument("--suffix", help="Thumbs filename suffix", default="_thumb")
    parser.add_argument("--width", help="Thumb width", type=int, default=150)
    parser.add_argument("--height", help="Thumb height", type=int, default=150)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity",
                    action="store_true")
    args = parser.parse_args()

    if not args.key:
        parser.print_help()
        return

    if not args.secret:
        parser.print_help()
        return

    if not args.url:
        parser.print_help()
        return

    if not args.filename:
        parser.print_help()
        return

    thumbs = ThumbS3(args.key, args.secret, args.url, args.width, args.height)
    thumbs.setDestinationFolder(args.folder)
    thumbs.setSuffix(args.suffix)
    if args.verbose:
        thumbs.setVerbose()
    thumbs.create(args.filename)
    return


if __name__ == '__main__':
    main()

