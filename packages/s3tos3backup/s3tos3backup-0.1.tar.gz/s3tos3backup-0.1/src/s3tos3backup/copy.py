import logging

from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.key import Key
from Queue import LifoQueue

from .worker import BaseWorker, add_keys_to_worker

log = logging.getLogger('s3tos3backup.remove')


class Worker(BaseWorker):

    def __init__(self, queue, thread_id, aws_key, aws_secret_key,
                 src_bucket_name, dst_bucket_name, src_path, dst_path):
        super(Worker, self).__init__(queue, thread_id, aws_key, aws_secret_key)
        self.src_bucket_name = src_bucket_name
        self.dst_bucket_name = dst_bucket_name
        self.src_path = src_path
        self.dst_path = dst_path

    def __init_s3(self):
        self.conn = connect_s3(self.aws_key, self.aws_secret_key)
        self.srcBucket = self.conn.get_bucket(self.src_bucket_name)
        self.dstBucket = self.conn.get_bucket(self.dst_bucket_name)

    def run(self):
        while True:
            try:
                if self.done_count % 1000 == 0:  # re-init conn to s3 every 1000 copies as we get failures sometimes
                    self.__init_s3()
                key_name = self.queue.get()
                k = Key(self.srcBucket, key_name)
                dist_key = Key(self.dstBucket, k.key)
                if not dist_key.exists() or k.etag != dist_key.etag:
                    log.info('t%s: Copy: %s' % (self.thread_id, k.key))
                    acl = self.srcBucket.get_acl(k)
                    self.dstBucket.copy_key(k.key, self.src_bucket_name, k.key, storage_class=k.storage_class)
                    dist_key.set_acl(acl)
                else:
                    log.info('t%s: Exists and etag matches: %s' % (self.thread_id, k.key))
                self.done_count += 1
            except BaseException:
                log.exception('  t%s: error during copy' % self.thread_id)
            self.queue.task_done()


def copy_bucket(aws_key, aws_secret_key, src, dst):
    conn = connect_s3(aws_key, aws_secret_key)
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
    srcBucket = conn.get_bucket(src_bucket_name)

    log.info('Start copy of %s to %s' % (src, dst))

    try:
        conn.get_bucket(dst_bucket_name)
    except S3ResponseError:
        conn.create_bucket(dst_bucket_name)

    q = LifoQueue(maxsize=5000)

    for i in range(20):
        log.info('Adding worker thread %s for queue processing' % i)
        t = Worker(q, i, aws_key, aws_secret_key,
                   src_bucket_name, dst_bucket_name,
                   src_path, dst_path)
        t.daemon = True
        t.start()

    add_keys_to_worker(q, srcBucket, src_path)
