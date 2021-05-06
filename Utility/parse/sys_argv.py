from typing import Dict, Set, List, Tuple


def parse(sys_argv: List[str], *, mapping = {},
          allow_duplicates: bool = False) \
        -> Tuple[List[str], Set[str], Dict[str, str]]:
    """split command in form of 'List[str]' into arguments list, flags and
    options

    for example:
        a --b=foo c --d -- --e f
        will produce arguments:
            ['a','c','--e','f']
        flags:
            {'d'}
        and options:
            {'b':'foo'}

    Args:
        sys_argv, List[str]:
            for example: the sys.argv

        allow_duplicates, bool:
            if enabled, later options with same key will override the former.
            otherwise, raise error if duplicated options were found.

    Returns:
        arguments, List[str]:
            for example, ['a','c','--e','f']

        flags, Set[str]
            for example, {'d'}

        options, Dict[str, str]:
            for example, {'b':'foo'}
    """

    arguments = []
    flags = set()
    options = {}
    doubledashed = False

    for v in sys_argv:
        if v.startswith('-') and not v.startswith('--'):
            v = v[1:].split('=', maxsplit=1)
            v = '--' + mapping[v[0]] + ('' if len(v) == 1 else '=' + v[1])
        if doubledashed or not v.startswith('--'):
            arguments.append(v)
        elif v == '--':
            doubledashed = True
        else:
            v = v[2:].split('=', maxsplit=1)
            if not allow_duplicates:
                assert v[0] not in {*flags, *options}, \
                    'duplicated option: %s' % v[0]
            if len(v) >= 2:
                options[v[0]] = v[1]
            else:
                flags.add(v[0])

    return arguments, flags, options
