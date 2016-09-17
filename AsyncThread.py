from threading import Thread
from queue import Queue
import time


q= Queue()

class C(Thread):
    def __init__(self,q):
        Thread.__init__(self)
        self.q = q


    def run(self):
        while True:
            b = self.q.get()
            print(b)
            self.q.task_done()
            time.sleep(2)




class P(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.q = q

    def run(self):
        while True:
            for i in range(5):

                self.q.put([i,i,i])
            self.q.join()
            time.sleep(8)
            # print("continue")
            print("QSIZE: ", self.q.qsize())


if __name__ == "__main__":
    p = P(q)
    c = C(q)
    p.start()
    c.start()
