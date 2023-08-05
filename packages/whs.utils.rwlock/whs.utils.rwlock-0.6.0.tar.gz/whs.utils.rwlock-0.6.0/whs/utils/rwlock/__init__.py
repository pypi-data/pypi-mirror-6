from threading import Condition, Lock
import uuid

class ReadingContext:
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.ticket = self.lock.get_ticket()
        self.lock.acquire_read(self.ticket)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release_read(self.ticket)
        return False

class WritingContext:
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.ticket = self.lock.get_ticket()
        self.lock.acquire_write(self.ticket)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release_write(self.ticket)
        return False

class ReadWriteLock:
    '''
    Many callers can acquire reading or writing at once, but no reading and
    writing can happen at the same time.
    '''
    def __init__(self):
        self._tickets_list = []
        self._readers_tickets = set()
        self._writers_tickets = set()
        self._list_has_shrinked = Condition()
        self._list_lock = Lock()

    def get_ticket(self):
        '''
        Get ticket for acquiring and releasing lock. Tickets should not be reused
        neither obtained other way then with this method.
        If above is ignored, behaviour is not defined.
        '''
        ticket = uuid.uuid4()
        self._list_lock.acquire()
        self._tickets_list.append(ticket)
        self._list_lock.release()
        return ticket

    def acquire_read(self, ticket):
        '''
        Acquire reading lock for this ticket. Waits until reading is possible,
        that is until all writers that acquired lock with tickets obtained
        before obtaining this ticket release lock.
        '''
        self._readers_tickets.add(ticket)
        while self._first_writer_ticket_no() < self._ticket_no(ticket):
            self._list_has_shrinked.acquire()
            self._list_has_shrinked.wait()
            self._list_has_shrinked.release()

    def release_read(self, ticket):
        '''
        Release reading lock for this ticket. Notifies writers to check whether
        it is possible to acquire writing lock (possibly not, if other readers
        hasn't released lock for their tickets).
        '''
        self._list_lock.acquire()
        self._tickets_list.remove(ticket)
        self._list_has_shrinked.acquire()
        self._list_has_shrinked.notifyAll()
        self._list_has_shrinked.release()
        self._list_lock.release()
        self._readers_tickets.remove(ticket)

    def acquire_write(self, ticket):
        '''
        Acquire writing lock for this ticket. Waits until writing is possible,
        that is until all readers that acquired lock with tickets obtained
        before obtaining this ticket release lock.
        '''
        self._writers_tickets.add(ticket)
        while self._first_reader_ticket_no() < self._ticket_no(ticket):
            self._list_has_shrinked.acquire()
            self._list_has_shrinked.wait()
            self._list_has_shrinked.release()

    def release_write(self, ticket):
        '''
        Release writing lock for this ticket. Notifies readers to check whether
        it is possible to acquire reading lock (possibly not, if other writers
        hasn't released lock for their tickets).
        '''
        self._list_lock.acquire()
        self._tickets_list.remove(ticket)
        self._list_has_shrinked.acquire()
        self._list_has_shrinked.notifyAll()
        self._list_has_shrinked.release()
        self._list_lock.release()
        self._writers_tickets.remove(ticket)

    def _first_reader_ticket_no(self):
        '''
        Internal method.
        Get number of first reading ticket on ticket list.
        '''
        for i in range(len(self._tickets_list)):
            if self._tickets_list[i] in self._readers_tickets:
                return i
        return len(self._tickets_list)

    def _first_writer_ticket_no(self):
        '''
        Similiar to _first_reader_ticket_no, but for writing tickets.
        '''
        for i in range(len(self._tickets_list)):
            if self._tickets_list[i] in self._writers_tickets:
                return i
        return len(self._tickets_list)

    def _ticket_no(self, ticket):
        '''
        Index of given ticket on ticket list.
        '''
        return self._tickets_list.index(ticket)

    def read(self):
        '''
        Get context manager for acquiring reading.
        '''
        return ReadingContext(self)

    def write(self):
        '''
        Get context manager for acquiring writing.
        '''
        return WritingContext(self)