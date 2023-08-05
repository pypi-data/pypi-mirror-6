from django.utils import six
from django.core.cache import cache
import cPickle as pickle
import functools
from django.db import models
from django.utils.importlib import import_module

class Property(property):
    pass

DNE = "!!!!DNE!!!!"
KEY_PREFIX = "FUNCTION_CACHE"
TIMEOUT = 100000

class invalidate(object):
    def __init__(self, func):
        self.signature = func
        self.func, self.post_save, self.post_delete, self.target_models = func(self)
    
    def contribute_to_class(self, cls, name):
        setattr(cls, name, self.func)
        setattr(cls, "__".join((name, 'post_save')), self.post_save)
        setattr(cls, "__".join((name, 'post_delete')), self.post_delete)
        setattr(cls, "__".join((name, 'context')), self)
        
        dispatch_uid = self.make_key("")
        
        for model in self.target_models:
            if model == 'self':
                model = cls
            elif isinstance(model, six.string_types):
                module, target = model.rsplit('.', 1)
                try:
                    mod = import_module(module)
                except ImportError:
                    model = None
                else:
                    model = getattr(mod, target, None)
                # this model doesn't exist yet, so setup a class_prepared signal
                if model is None:
                    def add_signals(sender, **kwargs):
                        if module == sender.__module__ and target == sender.__name__:
                            models.signals.post_save.connect(self.post_save, sender=sender, weak=False, dispatch_uid=dispatch_uid)
                            models.signals.post_delete.connect(self.post_delete, sender=sender, weak=False, dispatch_uid=dispatch_uid)
                    models.signals.class_prepared.connect(add_signals, weak=False, dispatch_uid=dispatch_uid)
                    continue

            if model is not None:
                models.signals.post_save.connect(self.post_save, sender=model, weak=False, dispatch_uid=dispatch_uid)
                models.signals.post_delete.connect(self.post_delete, sender=model, weak=False, dispatch_uid=dispatch_uid)

    def make_key(self, item_key):
        return ":".join((KEY_PREFIX, self.signature.__module__, self.signature.__name__, str(item_key)))
    def get(self, item_key):
        return cache.get(self.make_key(item_key), None)
    def set(self, item_key, value, timeout=None):
        timeout = timeout or TIMEOUT
        return cache.set(self.make_key(item_key), value, timeout)
    def delete(self, item_key):
        return cache.delete(self.make_key(item_key))
    def __contains__(self, item_key):
        return cache.get(self.make_key(item_key), None) is not None

def cached(key_func=None, timeout=None):
    key_func = key_func or (lambda *args, **kwargs: pickle.dumps((args, kwargs), pickle.HIGHEST_PROTOCOL))
    timeout = timeout or TIMEOUT
    def dec(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            key = f.make_key(key_func(*args, **kwargs))
            ret = cache.get(key, DNE)
            if ret == DNE:
                ret = func(*args, **kwargs)
                if callable(timeout):
                    tout = timeout(ret)
                else:
                    tout = timeout
                cache.set(key, ret, tout)
            return ret
        f.make_key = lambda item_key: ":".join((KEY_PREFIX, func.__module__, func.__name__, str(item_key)))
        f.compute = func
        return f
    return dec