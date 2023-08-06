'''raw data tracer for Coverage'''
import sys
import threading
import logging
import multiprocessing
log = logging.getLogger(__name__)

_SHOULD_TRACE = {}

def worker(read_end, ready_condition, dbhost, dbport, dbname):
    # the sub-process to dumping the events to mongo
    import threading; threading.settrace(None) # prevent tracing
    import Queue
    import ctl
    import gevent
    from gevent import monkey; monkey.patch_all(thread=True, aggressive=True)


    def tiny_worker(queue, dbhost, dbport, dbname):
        # feed events to mongo
        db = ctl.init(dbhost=dbhost, dbport=dbport, dbname=dbname)
        for events in iter(queue.get, 'STOP'):
            # convert list of event tuples to list of event dictionaries for mongo to process
            db_events = [{'file': filename, 'line': lineno} for filename, lineno in events]
            try:
                db.events.insert(db_events, w=0)
            except Exception as e:
                # FIXME dunno what else to do here
                pass
    
    def stop_workers(queue, workers):
        for worker in workers:
            queue.put('STOP')
        for worker in workers:
            worker.join()
        
    queue = Queue.Queue()
    #workers = [threading.Thread(target=tiny_worker, args=(queue, dbhost, dbport, dbname)) for i in range(10)]
    workers = [gevent.spawn(tiny_worker, queue, dbhost, dbport, dbname) for i in range(1000)]

    for worker in workers:
        worker.start() 
    ready_condition.acquire()
    ready_condition.notify()
    ready_condition.release()

    # process the fat pipe
    while True:
        try:
            events = read_end.recv()
        except EOFError, Exception:
            stop_workers(queue, workers)
            break
        if events == 'STOP':
            stop_workers(queue, workers)
            break
        try:
            queue.put(events)
        except Exception as e:
            # FIXME dunno what else to do here
            pass

class PyTracer(object):
    def __init__(self, dbhost="localhost", dbport=27017, dbname='moncov', blacklist=[], whitelist=[]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        self._should_process = getattr(sys.modules[__name__], '_SHOULD_TRACE')
        # a stack of line lists for caching inserts of executed lines
        self.stack = [[]]
        # uses 2 collections
        # - lines: indexed by filename,lineno; fields: hits count
        # - events: capped collection for short-term filename,lineno events
        #           storage
        # events is map-reduced to lines with the moncov stats commands
        try:
            from multiprocessing import Pipe, Process, Condition
            self.read_end, self.write_end = Pipe()
            ready_condition = Condition()
            self.worker = Process(target=worker, args=(self.read_end, ready_condition,
                                    dbhost, dbport, dbname))
            ready_condition.acquire()
            self.worker.start()
            ready_condition.wait()
            ready_condition.release()
            print 'working'
            

        except Exception as e:
            print >> sys.stderr, "%r, %r error: %r" % (__file__, self, e)
            #self.db = None
            self.enabled = False
            return
        else:
            self.enabled = True
            import atexit
            atexit.register(lambda: self.__del__())
        log.info('%r using: %r' % (self, (dbhost, dbport, dbname)))

    def __del__(self):
        try:
            print 'stopping %r' % self.worker
            self.write_end.send('STOP')
            self.write_end.close()
            self.worker.join(None)
        except:
            pass

    def _trace(self, frame, event, arg_unused):
        """The trace function passed to sys.settrace."""
        # reentrance not allowed
        if not self.enabled: #or not self.db:
            return self._trace

        filename, lineno = frame.f_code.co_filename, frame.f_lineno

        # needs processing?
        if filename not in self._should_process:
            # on black list?
            self.enabled = False # causes a call --- mask out
            self._should_process[filename] = \
                any([regexp.match(filename) for regexp in self.whitelist]) and \
                not any([regexp.match(filename) for regexp in self.blacklist])
            self.enabled = True
        if not self._should_process[filename]:
           return self._trace

        if event == 'call':
            # push new frame line insert list
            self.stack.append([{'file': filename, 'line': lineno}])
            return self._trace

        if event == 'return' or event == 'exception':
            # commit changes for current frame
            if not self.stack:
                return self._trace
            self.enabled = False # causes a call
            lines = self.stack.pop()
            if not lines:
                print >> sys.stderr, "no lines; bailing-out"
                sys.stderr.flush()
                return None
            try:
                #self.db.events.insert(lines, w=0)
                self.write_end.send(lines)
            except Exception as e:
                print >> sys.stderr, "%r, %r error: %r" % (__file__, self, e)
            finally:
                self.enabled = True
            if event == 'exception':
                self.stack.append([])
            return self._trace

        if event != 'line':
            # c_* events not processed
            return self._trace

        # add filename,lineno to processing list
        # self.stack[-1].append({"file": filename, "line": lineno})
        self.stack[-1].append((filename, lineno))
        return self._trace

    def start(self):
        """Start this Tracer."""
        self.enabled = True
        sys.settrace(self._trace)
        return self._trace

    def stop(self):
        """Stop this Tracer."""
        self.enabled = False
        sys.settrace(None)

    def get_stats(self):
        """Return a dictionary of statistics, or None."""
        return None


