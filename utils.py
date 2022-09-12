'''miscellaneous utility functions'''

def sqlite_typename(typ: type) -> str:
    if issubclass(typ, int):
        return "INT"
    elif issubclass(typ, float):
        return "REAL"
    elif typ == str:
        return "TEXT"
    raise ValueError(None, "types for stats must be str, bool, int, or float")