#!/usr/bin/env python3

from collections import defaultdict
from functools import partial, wraps


class SignalControl(Exception):
    '''Base type of signal control exceptions'''


class Disconnect(SignalControl):
    '''Handlers which raise this exception will be disconnected from the
    active signal'''


class StopPropagation(SignalControl):
    '''When this exception is raised by a handler no further handlers will
    be called for the active signal'''


def weak(meth, exception=Disconnect):
    '''Adapt a bound method to not count towards the refcount.

    Useful in e.g UI code where a view wants updates from a model but don't
    want that subscription to keep the widget around after closing the view.

    It works by holding a reference to the underlying function and creating a
    weakref to the bound `self` of the method. When the callback is called if
    the instance is no longer alive a `Disconnect` will be raised to the
    publish loop.
    '''

    import weakref

    try:  # python 3
        fun = meth.__func__
        ref = meth.__self__
    except AttributeError as e:  # python 2
        fun = meth.im_func
        ref = meth.im_self

    # precompute some strings that rely on the bound to object.
    srpr = repr(ref)
    funpath = '.'.join((
        fun.__module__,
        ref.__class__.__name__,
        fun.__name__))

    # Drop hard references to the bound object.
    ref = weakref.ref(ref)
    del meth

    def weak_method(*args, **kwargs):
        '''weakly bound method %s of %r''' % (funpath, srpr)

        obj = ref()
        if obj is None:
            raise exception("%s called on dead object" % funpath)

        return fun(obj, *args, **kwargs)

    return weak_method


def subscribers(obj, event):
    '''Get a list of all subscribers to `event` on `obj`'''

    if not hasattr(obj, '_subscribers'):
        obj._subscribers = defaultdict(list)

    return obj._subscribers[event]


def subscribe(obj, event, subscriber):
    '''Add a subscriber to `event` on `obj`'''

    subscribers(obj, event).append(subscriber)


def disconnect(obj, event, subscriber):
    '''Disconnect a subscriber to `event` on `obj`'''

    subscribers(obj, event).remove(subscriber)


def variants(obj, event):
    '''Get a generator that yields variations of a event.'''

    if hasattr(event, 'parameters'):
        parent = event.parent
        l = len(event.parameters)
        for i in range(l+1):
            sig, _ = parent.parameterise(event.parameters[:l-i])
            yield sig.__get__(obj)
    else:
        yield event
        if hasattr(event, 'name'):
            yield event.name


def _publish(obj, _event, **kwargs):
    '''Invoke all subscribers to `event` on `obj`

        Two flowcontrol exceptions exist that may be raised by subscribers
         * `Disconnect`
            A subscriber raising this exception will not be notified of
            this event further
         * `StopPropagation`
            Immediatly breaks the publish loop, no other subscribers will
            be notified.

        All other exceptions will be passed to the parent context and will
        break the publish loop without notifing remaining subscribers
    '''

    for var in variants(obj, _event):
        subs = subscribers(obj, var)
        disconnected = []
        try:
            for sub in subs:
                try:
                    sub(**kwargs)
                except Disconnect:
                    disconnected.append(sub)
                except StopPropagation:
                    break
        finally:
            for d in disconnected:
                subs.remove(d)


@wraps(_publish, ['__doc__'])
def publish(obj, _event, **kwargs):
    # Dispatch through broker if one is available
    try:
        publish = obj.publish
    except AttributeError:
        return _publish(obj, _event, **kwargs)
    else:
        return publish(_event, **kwargs)


class Broker(object):
    ''' Mixin with event publish/subscribe methods'''

    subscribe = subscribe
    disconnect = disconnect
    publish = _publish


class boundsignal(object):
    '''A signal that when published calls all of its subscribers'''

    def __init__(self, signal, im_self):
        self.__signal = signal
        self.__im_self = im_self
        self.name = self.__signal.name

        # Copy psignal attributes if available
        try:
            self.parent = self.__signal.parent
            self.parameters = self.__signal.parameters
        except AttributeError:
            pass

    def subscribe(self, subscriber):
        '''Subscribe a callback to this event'''
        subscribe(self.__im_self, self, subscriber)

    def disconnect(self, subscriber):
        '''Disconnect a callback from this event'''
        disconnect(self.__im_self, self, subscriber)

    def publish(self, **kwargs):
        '''Publish this event on `obj`'''
        publish(self.__im_self, self, **kwargs)

    def __call__(self, *args, **kwargs):
        '''parameterise and publish'''

        if self.__signal.parameter_def:
            sig, args = self.__signal.parameterise(args)
            sig = sig.__get__(self.__im_self)

            if len(kwargs) == 0:
                return sig
        else:
            sig = self

        sig.publish(**kwargs)

    def __hash__(self):
        return hash(self.__signal) ^ hash(self.__im_self)

    def __eq__(self, other):
        try:
            osignal = other.__signal
            oself = other.__im_self
        except AttributeError:
            return False

        return (self.__signal == osignal and self.__im_self == oself)

    def __repr__(self):
        return '<bound signal of %r, %r at 0x%r>' % (self.__im_self, self.__signal, id(self))


def binding(cls, fun):
    '''Create a proxy to `fun` that binds to `cls`

    When the proxy is called it dispatches to `fun` with a new instance of
    `cls` as the first argument. The new instance is created from the 1st and
    2nd argument to the proxy. The remaining arguments is forwarded to the
    original function.
    '''

    @wraps(fun)
    def bound(self, obj, *args, **kwargs):
        fun(cls(self, obj), *args, **kwargs)

    return bound


class signal(object):
    '''Publish/Subscribe pattern in a descriptor

    By creating a class member of this type you are enabling the class
    to publish events by that name for others to subscribe too
    '''

    def __init__(self, name=None, *parameters):
        self.name = name
        self.parameter_def = parameters

    def __get__(self, obj, objtype=None):
        '''Descriptor protocol

        returns self wrapped in a `boundsignal` when accessed from a
        instance
        '''

        if obj is None:
            return self
        return boundsignal(self, obj)

    subscribe = binding(boundsignal, boundsignal.subscribe)
    disconnect = binding(boundsignal, boundsignal.disconnect)
    publish = binding(boundsignal, boundsignal.publish)

    def parameterise(self, args):
        '''Create a parameterisation of this signal.'''

        sig = psignal(self, args[:len(self.parameter_def)])
        remainder = args[len(self.parameter_def):]
        return (sig, remainder)

    def __call__(self, *args, **kwargs):
        '''Parameterise and publish.'''

        if self.parameter_def:
            sig, args = self.parameterise(args)

            if len(args) == 0:
                return sig
        else:
            sig = self

        obj, = args
        sig.publish(obj, **kwargs)

    def __repr__(self):
        cls = self.__class__.__name__
        return '<%s(%s) at 0x%r>' % (cls, self.name or '', id(self))


class psignal(signal):
    '''A signal with defined parameters.

    Should not be created directly but by creating a `signal` with parameters
    and then calling it to define them which results in a new `psignal` being
    created.
    '''

    def __init__(self, parent, parameters):
        # Check invariants to short circuit otherwise horrible debug sessions
        assert not isinstance(parent, boundsignal)
        assert not hasattr(parent, 'parent')

        signal.__init__(self, parent.name, *parent.parameter_def)
        self.parent = parent
        self.parameters = tuple(parameters)
        self._complete = len(parameters) == len(self.parameter_def)
        hash(self.parameters)

    def __hash__(self):
        # the hash of the empty tuple is include so that a psignal with no
        # parameters hash to the same value as its signal type.
        return hash(self.parent) ^ hash(self.parameters) ^ hash(())

    def __call__(self, obj, **kwargs):
        '''Publish signal

        This should only be done for fully defined parameterisations, if
        called on a instance that is not fully defined `TypeError` is raised.
        '''
        if not self._complete:
            raise TypeError("Parameters not fully defined %r" % self)
        self.publish(obj, **kwargs)

    def __eq__(self, other):
        try:
            oparent = other.parent
            oparams = other.parameters
        except AttributeError:
            # Compare equal to signal type when no parameters are defined
            return self.parent is other and self.parameters == ()

        return self.parent == oparent and self.parameters == oparams

    def __repr__(self):
        cls = self.__class__.__name__
        return '<%s(%s)[%r] at 0x%r>' % (cls, self.name or '', self.parameters, id(self))


if __name__ == '__main__':  # pragma: no cover
    import logging
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger().info

    class Bar:
        throb = signal()

    bar = Bar()

    # When subscribing through a instance the context is automaticly set to
    # that instance.
    bar.throb.subscribe(lambda: log('hello'))
    # but it's also possible to subscribe with the signal type and pass the
    # instance as the first argument
    Bar.throb.subscribe(bar, lambda: log('world!'))

    # Both callbacks are executed
    bar.throb()

    # The Foo class show-case two ways signals can be reused and proxied from
    # other objects
    class Foo:
        method_two = signal()
        throb = Bar.throb

        def __init__(self, bar):
            # A simple alias is created by just copying the signal, note that
            # the context will still be the Bar instance
            self.method_one = bar.throb

            # Alternativly a proxy signal can be setup that subscribes to the
            # original signal
            bar.throb.subscribe(self.method_two)

    foo = Foo(bar)
    foo.method_one.subscribe(lambda: log('spam'))
    foo.method_two.subscribe(lambda: log('egg'))
    foo.throb.subscribe(lambda: log('bacon'))

    # Executes the spam and egg callbacks in addition the previous
    bar.throb()

    # Only executes the bacon callback
    foo.throb.publish()
