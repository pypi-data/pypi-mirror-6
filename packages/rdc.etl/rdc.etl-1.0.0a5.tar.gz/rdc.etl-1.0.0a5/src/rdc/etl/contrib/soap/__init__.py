# ensure dependency is available
try:
    import suds
except ImportError, e:
    raise ImportError('Missing dependency: "suds" is required to use "' + __name__ + '".')
