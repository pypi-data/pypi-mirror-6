import sys # Used to get rid of py2/3 differences

# Blatantly stolen from the excellent `six` library
# Allows the same calls between python2 and python3
if sys.version_info[0] == 3:
    exec_ = __builtins__["exec"]
    raw_input = input
else:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")
