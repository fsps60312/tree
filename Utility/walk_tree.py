from typing import List
import os
import re


def dfs_print(root_path: str, regex_pattern: str, ignore_pattern: str, *,
              follow_symlinks: bool = False) -> None:
    """
    A
    ├── B
    │   └── D
    └── C
    A
    └──<found nothing>
    """

    dir_stk = []  # {name, it, flags, print_buf, last_buf}

    def go_down(dirname: str) -> None:
        dirpath = os.path.join(*(v['name'] for v in dir_stk), dirname)
        dir_stk.append({
            'name': dirname,
            'it': os.scandir(dirpath),
            'flags': set(),
            'print_buf': [dirname],
            'last_buf': []})

    def format_last(vlst: List[str]) -> List[str]:
        return [
            {0: '└── '}.get(i, '    ') + v
            for i, v in enumerate(vlst)]

    def format_intermediate(vlst: List[str]) -> List[str]:
        return [
            {0: '├── '}.get(i, '│   ') + v
            for i, v in enumerate(vlst)]

    def append_entry(v: List[str]) -> None:
        stkv = dir_stk[-1]
        entry = format_intermediate(stkv['last_buf'])
        if len(dir_stk) == 1:
            print(''.join(v + '\n' for v in entry), end='', flush=True)
        stkv['print_buf'].extend(entry)
        stkv['last_buf'] = v

    def go_up() -> bool:
        """return False if popped item was the last one"""

        stkv = dir_stk.pop()
        stkv['it'].close()
        if 'has_file' in stkv['flags']:
            entry = format_last(stkv['last_buf'])
            if len(dir_stk) == 0:
                print(''.join(v + '\n' for v in entry), end='', flush=True)
            else:
                dir_stk[-1]['flags'].add('has_file')
                append_entry(stkv['print_buf'] + entry)
        return len(dir_stk) > 0


    def append_file(filename: str) -> None:
        dir_stk[-1]['flags'].add('has_file')
        append_entry([filename])

    print(root_path, flush=True)
    go_down(root_path)
    while len(dir_stk) > 0:
        stkv = dir_stk[-1]
        try:
            dir_entry = next(stkv['it'])
        except StopIteration:
            if go_up():
                continue
            else:
                if 'has_file' not in stkv['flags']:
                    print('└──<found nothing>')
                break
        if dir_entry.is_dir(follow_symlinks=follow_symlinks):
            go_down(dir_entry.name)
        else:
            file_path = os.path.join(
                *(v['name'] for v in dir_stk), dir_entry.name)
            if not re.fullmatch(ignore_pattern, file_path) and \
                    re.fullmatch(regex_pattern, file_path):
                append_file(dir_entry.name)

def walk_and_print_tree(root_path: str, regex_pattern: str,
                        ignore_pattern: str) -> None:
    """print directory tree
    """

    dfs_print(root_path, regex_pattern, ignore_pattern)
