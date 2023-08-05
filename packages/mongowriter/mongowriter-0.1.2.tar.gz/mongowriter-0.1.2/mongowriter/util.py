from Queue import Queue
from collections import defaultdict, deque


class TailDropMultiQueue(Queue):
    def __init__(self, maxgroupsize, maxsize=-1):
        Queue.__init__(self, maxsize=maxsize)
        self._maxgroupsize = maxgroupsize
        self.queues = defaultdict(deque)

    def _put(self, item):
        q = self.queues[item[0]]
        if len(q) < self._maxgroupsize:
            Queue._put(self, q)
        else:
            q.popleft()
        q.append(item)

    def _get(self):
        q = Queue._get(self)
        item = q.popleft()
        if len(q) == 0:
            del self.queues[item[0]]
        return item
