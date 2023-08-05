import logging

TRACE = 5
logging.addLevelName(TRACE, 'TRACE')

def trace(self, message, *args, **kws):
    self.log(TRACE, message, *args, **kws)
logging.Logger.trace = trace
