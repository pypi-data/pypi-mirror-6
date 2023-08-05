from __future__ import unicode_literals

import django.core.cache
from django.db import models
from django.db.models.manager import ManagerDescriptor
from django.utils.encoding import force_text

no_arg = object()

class CacheController(object):
    """ Automatically caches model instances on saves
    """
    DNE = 'DOES_NOT_EXIST'
    DEFAULT_TIMEOUT = 60 * 60 * 24 * 7

    def __init__(self, keys=('pk',), compute_fun=None, backend='default', timeout=no_arg):
        self.keys = keys
        
        if compute_fun is None:
            self.compute_obj = lambda **kwargs: self.model.objects.get(**kwargs)
        else:
            self.compute_obj = lambda **kwargs: getattr(self.model, compute_fun)(**kwargs)
        
        if backend is 'default':
            self.cache = django.core.cache.cache
        else:
            self.cache = django.core.cache.get_cache(backend)

        if timeout is no_arg:
            self.timeout = self.DEFAULT_TIMEOUT
        else:
            self.timeout = timeout

    def make_key(self, **kwargs):
        parts = [self.model._meta.app_label, self.model.__name__]
        for key in self.keys:
            parts.append(":".join((key, force_text(kwargs[key]))))
        return ":".join(parts)

    def get(self, **kwargs):
        key = self.make_key(**kwargs)
        obj = self.cache.get(key)
        if obj is None:
            try:
                obj = self.compute_obj(**kwargs)
            except self.model.DoesNotExist:
                self.cache.set(key, self.DNE, self.timeout)
                raise
            self.cache.set(key, obj, self.timeout)
        elif obj == self.DNE:
            raise self.model.DoesNotExist()
        return obj

    def contribute_to_class(self, model, name):
        self.model = model

        # The ManagerDescriptor attribute prevents this controller from being accessed via model instances.
        setattr(model, name, ManagerDescriptor(self))
        
        self.add_signals(model)

    def add_signals(self, model):
        #models.signals.pre_save.connect(self.pre_save, sender=model)
        models.signals.post_save.connect(self.post_save, sender=model)
        models.signals.post_delete.connect(self.post_delete, sender=model)
        
    def pre_save(self, instance, **kwargs):
        #TODO: get instance values of fresh object, before they were modified
        kwargs = {key:getattr(instance, key) for key in self.keys}
        key = self.make_key(**kwargs)
        obj = self.cache.get(key)
        self.cache.set(key, obj, timeout=getattr(self.cache, 'HERD_DELAY', 30))

    def post_save(self, instance, **kwargs):
        kwargs = {key:getattr(instance, key) for key in self.keys}
        key = self.make_key(**kwargs)
        new_obj = self.compute_obj(**kwargs)
        self.cache.set(key, new_obj, timeout=self.timeout)

    def post_delete(self, instance, **kwargs):
        kwargs = {key:getattr(instance, key) for key in self.keys}
        key = self.make_key(**kwargs)
        self.cache.set(key, self.DNE, timeout=self.timeout)


