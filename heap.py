import heapq


class MaxHeap(object):
    """Max Heap class that supports deletion (heapify doesn't support deletion of a key)"""

    def __init__(self):
        self.heap = []
        heapq.heapify(self.heap)
        self.deleted = {}

    def push(self,x):
        #Assert that x is not present or is deleted
        assert (-1*x not in self.deleted or self.deleted[-1*x])
        heapq.heappush(self.heap,-1*x)
        self.deleted[-1*x] = 0

    def max(self):
        if len(self.heap) == 0:
            return -1

        while self.deleted[self.heap[0]]:
            heapq.heappop(self.heap)
        return -1*self.heap[0]

    def delete(self,x):
        #Assert that x is present in heap
        assert (-1*x in self.deleted and not self.deleted[-1*x])

        #Check if x is the first element. If yes, then directly pop it from the heap
        if -1*x == self.heap[0]:
            heapq.heappop(self.heap)

        self.deleted[-1*x] = 1


