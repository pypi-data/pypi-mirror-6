def marlin_function(funct):
    try:
        from marlin import app
    except ImportError:
        from marlin.marlin import app
    from flask import Response

    def inner(*args, **kwargs):
        print "Arguments were: %s, %s" % (args, kwargs)
        return funct(*args, **kwargs)
    return inner
