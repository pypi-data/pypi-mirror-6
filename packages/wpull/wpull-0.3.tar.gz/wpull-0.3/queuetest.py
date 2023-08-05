import collections
import queue

MyTuple = collections.namedtuple('MyTuple', ['queue', 'queue1'])

tuple_instance = MyTuple(queue.Queue(), queue.Queue())

tuple_instance.queue.put(1)
tuple_instance.queue1.put(1)
