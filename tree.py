from Utility.parse.sys_argv import parse as sys_argv_parse
from Utility.walk_tree import walk_and_print_tree
import os
import sys

if __name__ == '__main__':
    print('sys.argv = %s' % sys.argv, file=sys.stderr)
    sys_args, sys_flags, sys_options = sys_argv_parse(
        sys.argv[1:], mapping={'P': 'pattern', 'I': 'ignore'})

    if not (len(sys_args) <= 1 and
            all(k in set() for k in sys_flags) and
            all(k in {'pattern', 'ignore'} for k in sys_options)):
        print('usage:\n' +
              f'    {sys.argv[0]} path --pattern=regex_pattern\n' +
              f'    {sys.argv[0]} --pattern=regex_pattern -- path\n',
              file=sys.stderr)
        print('found:\n' +
              f'    args: {sys_args}\n' +
              f'    flags: {sys_flags}\n' +
              f'    options: {sys_options}',
              file=sys.stderr)
        os._exit(0)

    root_path = sys_args[0] if len(sys_args) >= 1 else '.'
    regex_pattern = sys_options.get('pattern', '.*')
    ignore_pattern = sys_options.get('ignore', '(?!.*)')
    print('root_path:', repr(root_path), file=sys.stderr)
    print('regex_pattern:', repr(regex_pattern), file=sys.stderr)
    print('ignore_pattern:', repr(ignore_pattern), file=sys.stderr)
    walk_and_print_tree(root_path, regex_pattern, ignore_pattern)
