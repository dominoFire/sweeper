import Queue
import time


def test1():
    q = Queue.Queue(maxsize=10)

    for i in range(10):
        print 'Putting', i
        q.put(i)

    while not q.empty():
        e = q.get()
        #q.task_done()
        print 'getting', e


def test2():
    q = Queue.Queue(maxsize=10)

    for i in range(10):
        print 'Putting', i
        q.put(i)

    for i in range(10):
         q.task_done()
    #     time.sleep(2)

    q.join()


if __name__ == '__main__':
    test1()
    test2()
