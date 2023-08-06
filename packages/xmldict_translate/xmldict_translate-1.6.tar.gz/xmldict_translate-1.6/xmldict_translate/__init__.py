import sys
if sys.version.startswith('2'):
    from xmldict_translate import *
    from xmldict_translate import __version__
    from xmldict_translate import __author__
    from xmldict_translate import __author_email__
else:
    from .xmldict_translate import *
    from .xmldict_translate import __version__
    from .xmldict_translate import __author__
    from .xmldict_translate import __author_email__
