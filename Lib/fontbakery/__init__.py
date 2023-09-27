try:
    from ._version import version as __version__  # pytype:disable=import-error
except ImportError:
    __version__ = "0.0.0+unknown"
