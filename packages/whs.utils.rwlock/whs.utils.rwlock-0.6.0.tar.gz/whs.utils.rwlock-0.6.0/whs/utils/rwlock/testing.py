'''
Output should not be shattered, meaning full blocks should be sequential

r A ----
r B ----
r A ====
r B ====
w A ----
w A ====
is correct (read and write blocks are not shattered)

r A ----
w A ----
r A ====
r B ----
r B ====
w A ====
is incorrect (read block is interrupted by write block)
'''

import random
from threading import *
import time
from whs.utils.rwlock import ReadWriteLock

MAX=5
DEST_CNT = 2

def writer(data, lock):
    id = current_thread().name
    if not id in data:
        data[id] = []
    for i in range(MAX):
        ticket = lock.get_ticket()
        lock.acquire_write(ticket)
        print("w %s ------------" % id)
        print("w %s 1" % id)
        print("w %s 2" % id)
        data[id].append(i)
        print("w %s 3" % id)
        print("WRITER %s data %s" %(id, data) )
        print("w %s 4" % id)
        print("w %s ============" % id)
        lock.release_write(ticket)
        time.sleep(random.random()*2)

def reader(data, lock, watched_id):
    consumed = 0
    while consumed<MAX:
        ticket = lock.get_ticket()
        lock.acquire_read(ticket)
        reading = False
        if len(data[watched_id])>consumed:
            print("r %s ------------" % watched_id)
            print("r %s 1" % watched_id)
            taken = data[watched_id][0]
            print("r %s 2" % watched_id)
            consumed += 1
            print("r %s 3" % watched_id)
            print("READER %s taken %s for %s time" % (watched_id, taken, consumed))
            reading = True
            print("r %s 4" % watched_id)
            print("r %s ============" % watched_id)
        lock.release_read(ticket)
        if not reading:
            time.sleep(random.random()*2)

if __name__=="__main__":
    data = {}
    lock = ReadWriteLock()
    threads = []
    for tidx in range(DEST_CNT):
        w = Thread(target=writer, args=(data, lock))
        threads.append(w)
        r = Thread(target=reader, args=(data, lock, w.name))
        threads.append(r)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

