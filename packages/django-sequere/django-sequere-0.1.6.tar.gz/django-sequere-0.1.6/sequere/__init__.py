version = (0, 1, 6)

__version__ = '.'.join(map(str, version))

from .registry import register, autodiscover


__all__ = ['register', 'autodiscover']
