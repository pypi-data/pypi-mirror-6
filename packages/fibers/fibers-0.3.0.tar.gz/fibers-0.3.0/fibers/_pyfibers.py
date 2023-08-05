
import _continuation
import threading

__all__ = ['Fiber', 'error', 'current']


_tls = threading.local()


def current():
    try:
        return _tls.current_fiber
    except AttributeError:
        _create_main_fiber()
        return _tls.current_fiber


class error(Exception):
    pass


class Fiber(object):
    _cont = None
    _thread_id = None
    _ended = False

    def __init__(self, target=None, args=[], kwargs={}, parent=None):
        def _run(c):
            _tls.current_fiber = self
            try:
                return target(*args, **kwargs)
            finally:
                cont = self._cont
                self._cont = None
                self._ended = True
                parent = self.parent
                while True:
                    if parent is not None and parent._cont is not None and not parent._ended:
                        break
                    parent = parent.parent
                _continuation.permute(cont, parent._cont)

        self._func = _run

        if parent is None:
            parent = current()
        self._thread_id = threading.current_thread().ident
        if self._thread_id != parent._thread_id:
            raise error('parent cannot be on a different thread')
        self.parent = parent

    @classmethod
    def current(cls):
        return current()

    def _get_parent(self):
        return self.__dict__.get('parent', None)
    def _set_parent(self, value):
        if not isinstance(value, Fiber):
            raise TypeError('parent must be a Fiber')
        if value._ended:
            raise ValueError('parent must not have ended')
        if self._thread_id != value._thread_id:
            raise ValueError('parent cannot be on a different thread')
        self.__dict__['parent'] = value

    parent = property(_get_parent, _set_parent)
    del _get_parent, _set_parent

    def switch(self, value=None):
        if self._ended:
            raise error('Fiber has ended')

        curr = current()
        if curr._thread_id != self._thread_id:
            raise error('Cannot switch to a fiber on a different thread')

        if self._cont is None:
            self._cont = _continuation.continulet(self._func)

        try:
            return curr._cont.switch(value=value, to=self._cont)
        finally:
            _tls.current_fiber = curr

    def throw(self, *args):
        if self._ended:
            raise error('Fiber has ended')

        curr = current()
        if curr._thread_id != self._thread_id:
            raise error('Cannot switch to a fiber on a different thread')

        if self._cont is None:
            # Fiber was not started yet, propagate to parent directly
            self._ended = True
            parent = self.parent
            while True:
                if parent is not None and parent._cont is not None and not parent._ended:
                    break
                parent = parent.parent
            return parent.throw(*args)

        try:
            return curr._cont.throw(*args, to=self._cont)
        finally:
            _tls.current_fiber = curr

    def is_alive(self):
        return (self._cont is not None and self._cont.is_pending()) or \
               (self._cont is None and not self._ended)

    def __getstate__(self):
        raise TypeError('cannot serialize Fiber object')


def _create_main_fiber():
    main_fiber = Fiber.__new__(Fiber)
    main_fiber._cont = _continuation.continulet.__new__(_continuation.continulet)
    main_fiber._is_started = True
    main_fiber._thread_id = threading.current_thread().ident
    main_fiber.__dict__['parent'] = None
    _tls.main_fiber = main_fiber
    _tls.current_fiber = main_fiber

