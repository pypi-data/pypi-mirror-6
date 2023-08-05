# -*- coding: utf-8 -*-
from decorated.function import Function
import time

class retries(Function):
    def _init(self, times, delay=0):
        self._times = times
        self._delay = delay
        
    def _call(self, *args, **kw):
        for _ in range(self._times):
            try:
                return super(retries, self)._call(*args, **kw)
            except Exception as e:
                last_error = e
                time.sleep(self._delay)
        else:
            raise last_error
        