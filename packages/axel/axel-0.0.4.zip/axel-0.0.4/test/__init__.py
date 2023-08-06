import sys, axel, unittest, time, threading
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

try:
    threading.stack_size(64*1024)
except:
    pass
        
wait = 0

class EventTester(object):
    def __init__(self):
        self.event_1 = axel.Event(self)
        self.event_2 = axel.Event(self)
        self.event_3 = axel.Event(self)                
        self.wait = 0
    
    def on_event_1(self, sender, *args, **kw):
        assert isinstance(sender, EventTester)
        if self.wait:
            time.sleep(self.wait)
        return (args, kw)
        
    def on_event_2(self, sender, *args, **kw):
        assert isinstance(sender, EventTester)
        if self.wait:
            time.sleep(self.wait)
        return (args, kw)
    
    def on_event_3(self, sender, *args, **kw):
        assert isinstance(sender, EventTester)
        if self.wait:
            time.sleep(self.wait)
        return (args, kw)    

def on_event_1(sender, *args, **kw):
    assert isinstance(sender, EventTester)
    if wait:
        time.sleep(wait)
    return (args, kw)
    
def on_event_2(sender, *args, **kw):
    assert isinstance(sender, EventTester)
    if wait:
        time.sleep(wait)
    return (args, kw)

def on_event_3(sender, *args, **kw):
    assert isinstance(sender, EventTester)
    if wait:
        time.sleep(wait)
    return (args, kw)    
    
    
class TestAxel(unittest.TestCase):    
    def setUp(self):
        self.et = EventTester()
        self.et.event_1 += self.et.on_event_1
        self.et.event_2 += self.et.on_event_2
        self.et.event_3 += self.et.on_event_3
        
        self.et.event_1 += on_event_1
        self.et.event_2 += on_event_2
        self.et.event_3 += on_event_3
        
    def test_default(self):
        result = self.et.event_1(10, 20, p3=30)
        for r in result:
            self.assertEqual(r[0], True)
            self.assertEqual(r[1], ((10, 20), {'p3':30}))
            
    def test_register_unregister(self):
        key = hash(on_event_1)
        self.assertTrue(key in self.et.event_1.handlers)
        self.et.event_1 -= on_event_1
        self.assertTrue(key not in self.et.event_1.handlers)

    def test_asynch(self):
        self.et.event_1.asynchronous = True
        result = self.et.event_1(10, 20)
        for r in result:
            self.assertEqual(r[0], None)
            self.assertEqual(r[1], None)

    def test_exc_info(self):
        self.et.event_1.exc_info = True
        self.et.event_1.traceback = True
        
        def on_event_1_error(sender, x, y):
            raise ValueError('Dummy error')
        
        self.et.event_1.clear()
        self.et.event_1 += on_event_1_error
        
        r = self.et.event_1(10, 20)[0]        
        self.assertTrue(isinstance(r[1][1], ValueError))
        self.assertEqual(str(r[1][1]), 'Dummy error')
                
    def test_memoize(self):
        self.et.event_1 += (on_event_1, True)
        self.et.event_1(10, 20)
        
        key = hash(on_event_1)  
        self.assertTrue(key in self.et.event_1.memoize)
        
    def test_timeout(self):
        global wait 
        wait = .5
        self.et.event_1.clear()
        self.et.event_1 += (on_event_1, True, .2)
        
        err = self.et.event_1(10, 20)[0][1]
        self.assertTrue(isinstance(err, RuntimeError))


class TestRapidEventQueueing(unittest.TestCase):
    """
    Test for investigating weird behaviour in rapid calls to events that are being queued.

    Contributed by Rob van der Most <Rob@rmsoft.nl>    
    
    Have an event to which a single method is registered. This method will put the arguments
    from the call on a queue. Call the event several times in rapid succession. Check that no
    weird behaviour occurs.
    """
    def setUp(self):
        self.queue = Queue()
        self.event_class = axel.Event

    def event_listener(self, *args, **kwargs):
        self.queue.put_nowait((args, kwargs))

    def test_rapid_calls(self):
        the_event = self.event_class()
        the_event += self.event_listener

        for value in range(300):
            the_event(value)

        last_value = -1
        try:
            while True:
                next_value = self.queue.get_nowait()[0][0]
                self.assertEqual(next_value, last_value+1)
                last_value = next_value

        except Empty:
            pass

        self.assertEqual(last_value, 299)

    def test_event_raise_blocks_until_ready(self):
        """
        Expect the call to the event will not return until all listeners are called.
        """
        the_event = self.event_class()
        the_event += self.event_listener

        for value in range(300):
            the_event(value)

            stored_value = self.queue.get_nowait()[0][0]
            self.assertEqual(value, stored_value)
                          
if __name__=='__main__':
    unittest.main()