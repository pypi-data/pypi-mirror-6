VERSION = (0, 2)
__version__ = '.'.join(map(str, VERSION))
DATE = "2014-04-24"
try:
    from . import conf
except:
    pass