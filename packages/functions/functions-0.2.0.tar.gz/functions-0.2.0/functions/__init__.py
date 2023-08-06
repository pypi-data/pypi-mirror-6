from functools import partial, wraps


__version__ = "0.2.0"


class MarshallingError(Exception):
    pass


def first(coll): # rewrite to use frozen dict
    """Return the first item in a dictionary, list, or tuple."""
    if not coll:
        return None
    try:
        return dict((coll.items()[0],))
    except AttributeError:
        return coll[0]


def last(coll): # rewrite to use frozen dict
    """Return the last item in a dictionary, list, or tuple."""
    try:
        return dict((coll.items()[-1],))
    except AttributeError:
        return coll[-1]


def rest(coll): # rewrite to use frozen dict
    """Return the remaining items in a dictionary, list, or tuple."""
    try:
        return dict(coll.items()[1:])
    except AttributeError:
        return coll[1:]


def none(*args, **kwargs):
    return None


identity = lambda x: x


def is_seq(x):
    """Return True if x is iterable."""
    return (not hasattr(x, "strip") and
            hasattr(x, "__getitem__") or
            hasattr(x, "__iter__"))


def fmap(f, coll):
    """Apply a function to each item in a dictionary, list, or tuple."""
    try:
        return {k: f(v) for k, v in coll.iteritems()}
    except AttributeError:
        func = tuple if isinstance(coll, tuple) else list
        return func(f(v) for v in coll)


def walk(f, form):
    """Traverse an arbitrary data structure and apply a function to each
    node."""
    return fmap(lambda v: f(v) if not is_seq(v) else walk(f, v), form)


def walk_keys(inner, outer, form):
    def process_node(k, v):
        if not isinstance(v, dict):
            try:
                return inner(k, v)
            except Exception:
                raise MarshallingError(("Cannot process node for key '{0}' and "
                                        "value '{1}'".format(k, v)))
        return inner(k, walk_keys(inner, identity, v))
    try:
        items = (process_node(k, v) for k, v in form.iteritems())
        return outer(dict(filter(lambda item: item is not None, items)))
    except AttributeError:
        seq_type = tuple if isinstance(form, tuple) else list
        return outer(seq_type(walk_keys(inner, identity, row) for row in form))


def cons(x, seq):
    """Return a tuple where x is the first element and seq is the rest."""
    return (x,) + seq


def thread(x, form):
    if isinstance(form, tuple):
        f, args = first(form), rest(form)
        return f(x, *args)
    return form(x)


def thread_first(x, form, *more):
    """Thread the expression through the forms."""
    if not more:
        return thread(x, form)
    return thread_first(*cons(thread(x, form), more))


def compose(*funcs):
    def compose2(f, g):
        if not callable(f):
            foo = partial(*f)
        else:
            foo = f
        if not callable(g):
            bar = partial(*g)
        else:
            bar = g
        return lambda x: foo(bar(x))
    return reduce(compose2, reversed(funcs))


def thread_last(x, *funcs):
    return compose(*funcs)(x)


def memoize(f):
    """Return a memoized version of a function."""
    cache = {}

    @wraps(f)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        rv = f(*args)
        cache[args] = rv
        return rv
    return wrapper


def frozendict(*keyvals):
    """Return an immutable dictionary"""
    return frozenset(keyvals)


def zipdict(keys, vals):
    """Return an immutable dictionary with keys mapped to corresponding
    values"""
    return frozendict(*zip(keys, vals))


def get(fdict, key, default=None):
    """Return the value mapped to a key, default or None if key not present"""
    try:
        return dict(fdict)[key]
    except KeyError:
        return default


def contains(fdict, key):
    return key in dict(fdict)


def find(fdict, key):
    try:
        return (key, dict(fdict)[key])
    except KeyError:
        return None


def keys(fdict):
    return tuple(dict(fdict).keys())


def vals(fdict):
    return tuple(dict(fdict).values())


def merge(*fdicts):
    """Merge two or more frozen dictionaries."""
    def items(fdict):
        return tuple(dict(fdict).items())
    if len(fdicts) == 2:
        return dict(items(first(fdicts)) + items(last(fdicts)))
    return merge(first(fdicts), apply(merge, rest(fdicts)))


def walk_replace(smap, form):
    def replace_at_node(k, v):
        if k in smap:
            return (smap[k], v)
        return (k, v)
    return walk_keys(replace_at_node, identity, form)


def union(*sets):
    return first(sets).union(*rest(sets))


def dict_invert(dict):
    def flip_node(k, v):
        return (v, k)
    return walk_keys(flip_node, identity, dict)
