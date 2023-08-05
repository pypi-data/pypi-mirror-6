from datetime import date
from boto import connect_s3

from .copy import copy_bucket
from .remove import remove_old_buckets


def run_backup(src, backup, remove, aws_key=None, aws_secret_key=None, remove_older_days=7):
    if aws_key and aws_secret_key:
        connection = connect_s3(aws_key, aws_secret_key)
    else:
        # IAM role connection
        connection = connect_s3()
    if backup:
        today = date.today()
        dest = src + '-backup-' + str(today)
        copy_bucket(connection, src, dest)
    if remove:
        remove_old_buckets(connection, src, remove_older_days)
