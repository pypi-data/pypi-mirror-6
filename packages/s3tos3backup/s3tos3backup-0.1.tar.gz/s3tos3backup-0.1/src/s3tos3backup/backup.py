from datetime import date

from .copy import copy_bucket
from .remove import remove_old_buckets


def run_backup(backup, remove, aws_key, aws_secret_key, remove_older_days):
    src = 'caseify-remi'
    if backup:
        today = date.today()
        dest = src + '-backup-' + str(today)
        copy_bucket(aws_key, aws_secret_key, src, dest)
    if remove:
        remove_old_buckets(aws_key, aws_secret_key, src, remove_older_days)
