import threading
import logging
import time

log = logging.getLogger('s3tos3backup.worker')


class BaseWorker(threading.Thread):
    def __init__(self, queue, thread_id, connection):
        threading.Thread.__init__(self)
        self.queue = queue
        self.done_count = 0
        self.thread_id = thread_id
        self.connection = connection

    def run(self):
        pass

MAX_KEYS = 1000


def add_keys_to_worker(q, bucket, src_path=''):
    result_marker = ''

    i = 0

    while True:
        log.info('Fetch next %s, backlog currently at %s, have done %s' % (MAX_KEYS, q.qsize(), i))
        try:
            keys = bucket.get_all_keys(max_keys=MAX_KEYS,
                                       marker=result_marker,
                                       prefix=src_path or '')
            if len(keys) == 0:
                break
            for k in keys:
                i += 1
                q.put(k.key)
            log.info('Added %s keys to queue' % len(keys))
            if len(keys) < MAX_KEYS:
                log.info('All items now in queue')
                break
            result_marker = keys[MAX_KEYS - 1].key
            while q.qsize() > (q.maxsize - MAX_KEYS):
                time.sleep(1)  # sleep if our queue is getting too big for the next set of keys
        except BaseException:
            log.exception('error during fetch, quitting')
            break

    log.info('Waiting for queue to be completed')
    q.join()
