import re


PARSE_STATIC_ASSETS_RE = re.compile('asset\s+(?P<name>[0-9a-z\.]+)')

PLIMDSL_PARSERS = tuple()
