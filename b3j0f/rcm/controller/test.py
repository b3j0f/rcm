from abc import ABCMeta

from inspect import isroutine, getmembers
from functools import wraps


class ProxyMeta(ABCMeta):

    def __call__(cls, bases, instance, *args, **kwargs):

        result = super(ProxyMeta, cls).__call__(*args, **kwargs)

        for base in bases:
            cls.register(base)
            for name, member in getmembers(base, lambda member: isroutine(member)):
                if not hasattr(cls, name):
                    try:
                        @wraps(member, {}, {})
                        def proxy(*args, **kwargs):
                            return getattr(instance, name)(*args, **kwargs)
                    except Exception as e:
                        print('exception on {0}, {1}'.format(name, e))
                    else:
                        setattr(cls, name, proxy)

        return result


class A(object):
    __metaclass__ = ProxyMeta


class Test(list):
    pass

test = Test()

a = A(bases=(dict, int), instance=test)

a.setdefault('a', 2)
print(a['a'])

a.append(0)
print(a[0])
