import logging

from boto.exception import S3ResponseError
from boto.s3.key import Key
from dateutil import parser
from datetime import date, timedelta
from Queue import LifoQueue

from .worker import BaseWorker, add_keys_to_worker

log = logging.getLogger('s3tos3backup.remove')


class Worker(BaseWorker):

    def __init__(self, queue, thread_id, connection, bucket):
        super(Worker, self).__init__(queue, thread_id, connection)
        self.bucket = bucket

    def run(self):
        while True:
            try:
                key_name = self.queue.get()
                k = Key(self.bucket, key_name)
                log.info('  t%s: Delete: %s' % (self.thread_id, k.key))
                self.bucket.delete_key(k.key)
                self.done_count += 1
            except Exception, e:
                log.exception('  t%s: error during remove: %s' % (self.thread_id, e))
            self.queue.task_done()


def remove_old_buckets(connection, src, number_of_days=7):
    max_date = date.today() - timedelta(days=int(number_of_days) - 1)
    log.info('Removing older backup than: %s' % max_date)

    buckets = connection.get_all_buckets()
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
                        t = Worker(q, i, connection, bucket)
                        t.daemon = True
                        t.start()

                    add_keys_to_worker(q, bucket)
                    bucket.delete()
