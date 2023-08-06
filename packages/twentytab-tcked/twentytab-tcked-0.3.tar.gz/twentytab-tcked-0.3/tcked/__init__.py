VERSION = (0, 3)
__version__ = '.'.join(map(str, VERSION))
DATE = "2014-01-08"
try:
    from . import conf
except:
    pass