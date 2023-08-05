"""Inserts documents passed through a queue into a mongo db. The queue
must contain tuples of (collection_name, document) that can be
directly inserted in mongo."""

import random
import logging

from Queue import Empty
from time import sleep
from threading import Thread
import socket

from pymongo import MongoReplicaSetClient
from pymongo.errors import AutoReconnect, ConnectionFailure, OperationFailure

logger = logging.getLogger(__name__)


def retry_on_exception(retries, exc, pause):
    def retry_on_exception_decorator(func):
        def wrapped(*fargs, **fkwargs):
            for _ in xrange(retries):
                try:
                    return func(*fargs, **fkwargs)
                except exc:
                    sleep(pause)
            else:
                return func(*fargs, **fkwargs)
        return wrapped
    return retry_on_exception_decorator


# replica set might be changing primary
@retry_on_exception(retries=14, exc=(ConnectionFailure, OperationFailure, socket.timeout), pause=5)
def init_client(**client_kwargs):
    return MongoReplicaSetClient(**client_kwargs)


@retry_on_exception(retries=14, exc=(ConnectionFailure, OperationFailure, socket.timeout), pause=5)
def authenticate_db(client, dbname, username, password):
    db = client[dbname]
    db.authenticate(username, password)
    return db


class MongoWriter(object):
    def __init__(self, queue, dbname, username, password=None, num_workers=10, manipulate=True, **client_kwargs):
        self.stopping = False
        self.queue = queue
        self.manipulate = manipulate

        client_kwargs.setdefault('max_pool_size', num_workers)

        self.client = init_client(**client_kwargs)
        self.db = authenticate_db(self.client, dbname, username, password)

        self.num_workers = num_workers
        self.workers = []

    def start(self):
        assert not len(self.workers)
        self.workers = [Thread(target=self.run) for _ in xrange(self.num_workers)]
        for w in self.workers:
            w.daemon = True
            w.start()

    def stop(self):
        self.stopping = True
        self.workers = []

    def run(self):
        while not (self.stopping and self.queue.empty()):
            try:
                collection, document = self.queue.get(timeout=5)
            except Empty:
                continue

            try:
                self._insert_line(collection, document)
            except Exception as e:
                logger.error('unknown exception ignored while inserting line: %r', e)
            finally:
                self.queue.task_done()

    def _insert_line(self, collection, document):
        while not self.queue.full():
            try:
                self.db[collection].insert(document, manipulate=self.manipulate)
                return
            except AutoReconnect:
                sleep(random.uniform(0.2, 1.0))
        else:
            logger.warning('Overloaded; dropping queued message %s', document)
