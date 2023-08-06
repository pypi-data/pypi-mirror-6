from cherrypy.wsgiserver import ThreadPool
from cherrypy.process.plugins import Monitor
from dynpool import DynamicPoolResizer


def get_pool_resizer(self, minspare=1, maxspare=5, shrinkfreq=10,
                     logger=None):
    return DynamicPoolResizer(self, minspare, maxspare, shrinkfreq, logger)


ThreadPool.size = property(lambda self: len(self._threads))
ThreadPool.get_pool_resizer = get_pool_resizer


class ThreadPoolMonitor(Monitor):

    def __init__(self, bus):
        self._run = lambda: None
        super(ThreadPoolMonitor, self).__init__(bus, self.run, frequency=1)

    def run(self):
        self._run()

    def configure(self, thread_pool, minspare, maxspare, shrinkfreq, logger):
        resizer = thread_pool.get_pool_resizer(
            minspare=minspare,
            maxspare=maxspare,
            shrinkfreq=shrinkfreq,
            logger=logger or (lambda: None)
        )
        self._run = resizer.run

    def stop(self):
        self._run = lambda: None
        super(ThreadPoolMonitor, self).stop()
    stop.priority = 10
