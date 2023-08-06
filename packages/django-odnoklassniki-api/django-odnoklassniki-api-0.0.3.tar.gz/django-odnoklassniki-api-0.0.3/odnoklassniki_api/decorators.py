# -*- coding: utf-8 -*-
from django.utils.functional import wraps
from django.db.models.query import QuerySet
import re

def opt_arguments(func):
    '''
    Meta-decorator for ablity use decorators with optional arguments
    from here http://www.ellipsix.net/blog/2010/08/more-python-voodoo-optional-argument-decorators.html
    '''
    def meta_wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            # No arguments, this is the decorator
            # Set default values for the arguments
            return func(args[0])
        else:
            def meta_func(inner_func):
                return func(inner_func, *args, **kwargs)
            return meta_func
    return meta_wrapper

@opt_arguments
def fetch_all(func, return_all=None, always_all=False):
    """
    Class method decorator for fetching all items. Add parameter `all=False` for decored method.
    If `all` is True, method runs as many times as it returns any results.
    Decorator receive parameters:
      * callback method `return_all`. It's called with the same parameters
        as decored method after all itmes are fetched.
      * `always_all` bool - return all instances in any case of argument `all`
        of decorated method
    Usage:

        @fetch_all(return_all=lambda self,instance,*a,**k: instance.items.all())
        def fetch_something(self, ..., *kwargs):
        ....
    """
    def wrapper(self, *args, **kwargs):

        if len(args) > 0:
            raise ValueError("It's prohibited to use non-key arguments for method decorated with @fetch_all, method is %s.%s(), args=%s" % (self.__class__.__name__, func.__name__, args))

        all = kwargs.pop('all', False) or always_all
        instances_all = kwargs.pop('instances_all', None)

        instances = func(self, **kwargs)
        if len(instances) == 2 and isinstance(instances, tuple):
            instances, response = instances

        if all:
            if isinstance(instances, QuerySet):
                if not instances_all:
                    instances_all = QuerySet().none()
                instances_all |= instances
            elif isinstance(instances, list):
                if not instances_all:
                    instances_all = []
                instances_all += instances
            else:
                raise ValueError("Wrong type of response from func %s. It should be QuerySet or list, not a %s" % (func, type(instances)))

            # resursive pagination
            if response['has_more']:
                return wrapper(self, all=all, instances_all=instances_all, anchor=response['anchor'], **kwargs)

            if return_all:
                kwargs['instances'] = instances_all
                return return_all(self, **kwargs)
            else:
                return instances_all
        else:
            return instances

    return wraps(func)(wrapper)

def opt_generator(func):
    """
    Class method or function decorator makes able to call generator methods as usual methods.
    Usage:

        @method_decorator(opt_generator)
        def some_method(self, ...):
            ...
            for count in some_another_method():
                yield (count, total)

    It's possible to call this method 2 different ways:

        * instance.some_method() - it will return nothing
        * for count, total in instance.some_method(as_generator=True):
            print count, total
    """
    def wrapper(*args, **kwargs):
        as_generator = kwargs.pop('as_generator', False)
        result = func(*args, **kwargs)
        return result if as_generator else list(result)
    return wraps(func)(wrapper)