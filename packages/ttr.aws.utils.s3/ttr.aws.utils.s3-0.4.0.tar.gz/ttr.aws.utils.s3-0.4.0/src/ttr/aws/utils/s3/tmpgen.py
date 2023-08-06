from __future__ import print_function
import plac
import boto
import time
import sys

def error(*objs):
    print("ERROR", *objs, end='\n', file=sys.stderr)

@plac.annotations(
        profile_name=("""Name of boto profile to use for credentials""", "option"),
        aws_access_key_id=("Your AWS Access Key ID", "option"),
        aws_secret_access_key=("Your AWS Secret Access Key", "option"),
        expire_dt="ISO formatted time of expiration, full seconds, 'Z' is obligatory, e.g. '2014-02-14T21:47:16Z'",
        bucket_name="name of bucket",
        key_names="key names to generate tmpurl for"
        )
def main(expire_dt, bucket_name, profile_name=None, aws_access_key_id=None,
        aws_secret_access_key=None, *key_names):
    """Generate temporary url for accessing content of AWS S3 key with defined expiration date-time.

    Urls are printed one per line to stdout.

    For missing key names empty line is printed and error goes to stderr.
    """
    expire = int(time.mktime(time.strptime(expire_dt, "%Y-%m-%dT%H:%M:%SZ"))) - time.timezone
    try:
        con = boto.connect_s3(profile_name=profile_name)
    except Exception as e:
        error("Unable to connect to AWS S3, check your credentials", e)
        return
    try:
        bucket = con.get_bucket(bucket_name)
    except boto.exception.S3ResponseError as e:
        error("Error: Bucket not found: ", bucket_name)
        return
    for key_name in key_names:
        key = bucket.get_key(key_name)
        if key is None:
            error("Error: missing key: ", key_name)
            print("")
        else:
            print(key.generate_url(expires_in=expire, expires_in_absolute=True))

def placer():
    try:
        plac.call(main)
    except Exception as e:
        error(e)
    
if __name__ == "__main__":
    placer()
