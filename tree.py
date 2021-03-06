from Utility.parse.sys_argv import parse as sys_argv_parse
# from Utility.walk_tree import walk_and_print_tree
from Utility.format_tree import TreeFormatter
import os
import sys
import re

if __name__ == '__main__':
    print('sys.argv = %s' % sys.argv, file=sys.stderr)
    sys_args, sys_flags, sys_options = sys_argv_parse(
        sys.argv[1:], mapping={'P': 'pattern', 'I': 'ignore'})

    if not (len(sys_args) <= 1 and
            all(k in {'show_empty'} for k in sys_flags) and
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

    root_path: str = sys_args[0] if len(sys_args) >= 1 else '.'
    regex_pattern: str = sys_options.get('pattern', '.*')
    ignore_pattern: str = sys_options.get('ignore', '(?!.*)')
    show_empty: bool = 'show_empty' in sys_flags
    print('root_path:', repr(root_path), file=sys.stderr)
    print('regex_pattern:', repr(regex_pattern), file=sys.stderr)
    print('ignore_pattern:', repr(ignore_pattern), file=sys.stderr)
    print('show_empty:', show_empty)

    for line in TreeFormatter(
            get_name=lambda v: v.name,
            get_iter=lambda _, v: os.scandir(v.path),
            walk_cond=lambda _, v: v.is_dir(follow_symlinks=False),
            print_cond=lambda _, v: (
                re.fullmatch(ignore_pattern, v.path) is None and
                re.fullmatch(regex_pattern, v.path) is not None),
            print_empty=show_empty).walk_from_name(
                root_path, os.scandir(root_path)):
        print(line)
