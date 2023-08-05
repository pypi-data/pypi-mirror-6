import logging

from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.key import Key
from dateutil import parser
from datetime import date, timedelta
from Queue import LifoQueue

from .worker import BaseWorker, add_keys_to_worker

log = logging.getLogger('s3tos3backup.remove')


class Worker(BaseWorker):

    def __init__(self, queue, thread_id, aws_key, aws_secret_key, bucket):
        super(Worker, self).__init__(queue, thread_id, aws_key, aws_secret_key)
        self.bucket = bucket

    def __init_s3(self):
        self.conn = connect_s3(self.aws_key, self.aws_secret_key)

    def run(self):
        while True:
            try:
                if self.done_count % 1000 == 0:  # re-init conn to s3 every 1000 copies as we get failures sometimes
                    self.__init_s3()
                key_name = self.queue.get()
                k = Key(self.bucket, key_name)
                log.info('  t%s: Delete: %s' % (self.thread_id, k.key))
                self.bucket.delete_key(k.key)
                self.done_count += 1
            except BaseException:
                log.exception('  t%s: error during copy' % self.thread_id)
            self.queue.task_done()


def remove_old_buckets(aws_key, aws_secret_key, src, number_of_days=7):
    max_date = date.today() - timedelta(days=int(number_of_days) - 1)
    log.info('Removing older backup than: %s' % max_date)

    conn = connect_s3(aws_key, aws_secret_key)
    buckets = conn.get_all_buckets()
    dst_prefix = src + '-backup-'

    for bucket in buckets:
        name = bucket.name
        if name.startswith(dst_prefix):
            date_name = name.split(dst_prefix)[1]
            bucket_date = parser.parse(date_name).date()
            if bucket_date < max_date:
                log.info('Remove bucket: %s' % name)
                try:
                    bucket.delete()
                except S3ResponseError:
                    log.info('Bucket not empty, removing files')
                    q = LifoQueue(maxsize=5000)

                    for i in range(20):
                        log.info('Adding worker thread %s for queue processing' % i)
                        t = Worker(q, i, aws_key, aws_secret_key,
                                   bucket)
                        t.daemon = True
                        t.start()

                    add_keys_to_worker(q, bucket)
                    bucket.delete()
