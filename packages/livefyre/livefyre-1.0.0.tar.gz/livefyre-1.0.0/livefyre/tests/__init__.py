import pkgutil, unittest

def all_names():
    for _, modname, _ in pkgutil.iter_modules(__path__):
        if modname.startswith('test_'):
            yield 'stripe.test.' + modname

def all():
    return unittest.defaultTestLoader.loadTestsFromNames(all_names())