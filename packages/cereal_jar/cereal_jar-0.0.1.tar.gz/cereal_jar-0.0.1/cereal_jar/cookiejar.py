import functools

import cereal_jar.util

_identity = lambda x:x
class cookiejar:
    load = functools.partial(cereal_jar.util.reader, _identity)
    dump = functools.partial(cereal_jar.util.writer, _identity)
