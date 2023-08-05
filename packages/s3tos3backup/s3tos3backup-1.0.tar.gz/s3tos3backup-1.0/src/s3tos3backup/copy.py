import logging

from boto.exception import S3ResponseError
from boto.s3.key import Key
from Queue import LifoQueue

from .worker import BaseWorker, add_keys_to_worker

log = logging.getLogger('s3tos3backup.remove')


class Worker(BaseWorker):

    def __init__(self, queue, thread_id, connection,
                 src_bucket_name, dst_bucket_name, src_path, dst_path):
        super(Worker, self).__init__(queue, thread_id, connection)
        self.src_bucket_name = src_bucket_name
        self.srcBucket = self.connection.get_bucket(src_bucket_name)
        self.dstBucket = self.connection.get_bucket(dst_bucket_name)

    def run(self):
        while True:
            try:
                key_name = self.queue.get()
                k = Key(self.srcBucket, key_name)
                dist_key = Key(self.dstBucket, k.key)
                if not dist_key.exists() or k.etag != dist_key.etag:
                    log.info('t%s: Copy: %s' % (self.thread_id, k.key))
                    self.dstBucket.copy_key(k.key, self.src_bucket_name, k.key, storage_class=k.storage_class,
                                            preserve_acl=True)
                else:
                    log.info('t%s: Exists and etag matches: %s' % (self.thread_id, k.key))
                self.done_count += 1
            except Exception, e:
                log.exception('  t%s: error during copy: %s' % (self.thread_id, e))
            self.queue.task_done()


def copy_bucket(connection, src, dst):
    try:
        (src_bucket_name, src_path) = src.split('/', 1)
    except ValueError:
        src_bucket_name = src
        src_path = None
    try:
        (dst_bucket_name, dst_path) = dst.split('/', 1)
    except ValueError:
        dst_bucket_name = dst
        dst_path = None
    if dst_path is not None:
        raise ValueError("not currently implemented to set dest path; must use default, which will mirror the source")
    srcBucket = connection.get_bucket(src_bucket_name)

    log.info('Start copy of %s to %s' % (src, dst))

    try:
        connection.get_bucket(dst_bucket_name)
    except S3ResponseError:
        connection.create_bucket(dst_bucket_name)

    q = LifoQueue(maxsize=5000)

    for i in range(20):
        log.info('Adding worker thread %s for queue processing' % i)
        t = Worker(q, i, connection,
                   src_bucket_name, dst_bucket_name,
                   src_path, dst_path)
        t.daemon = True
        t.start()

    add_keys_to_worker(q, srcBucket, src_path)
