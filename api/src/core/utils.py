class DotDict(dict):
    """Dot.notation access to dictionary attributes."""

    # pylint: disable=no-self-argument
    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if isinstance(val, dict) else val

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
