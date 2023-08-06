Resize images hosted on Amazon S3 using Pillow

## Installation

    pip install s3imageresize

## Usage

Make sure your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are exported as environmental variables

In code:

    from s3imageresize import resize_image_folder
    resize_image_folder(bucket_name, prefix, (width, height))

From the command line:

    s3resizeimagefolder.py bucketname prefix width height
