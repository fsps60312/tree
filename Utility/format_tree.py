from Utility.ansi_format import Ansi
from typing import List, Iterator, Callable, TypeVar, Generic, Final, Generator

T = TypeVar('T')


def indent_last(vlst: List[str]) -> List[str]:
    return [
        {0: '└── '}.get(i, '    ') + v
        for i, v in enumerate(vlst)]


def indent_intermediate(vlst: List[str]) -> List[str]:
    return [
        {0: '├── '}.get(i, '│   ') + v
        for i, v in enumerate(vlst)]


class StackEnv(Generic[T]):
    def __init__(self,
                 get_iter: Callable[[List[T], T], Iterator[T]],
                 get_name: Callable[[T], str],
                 print_empty: bool,
                 colorful: bool):
        self.get_iter = get_iter
        self.get_name = get_name
        self.print_empty = print_empty
        self.colorful = colorful


class StackNode(Generic[T]):
    def __init__(self, env: StackEnv[T], objlst: List[T], obj: T):
        self.env = env
        self.obj = obj
        self.it = self.env.get_iter(objlst, obj)
        self.has_sth = False
        self.name = Ansi.dircolor(self.env.get_name(obj)) \
            if self.env.colorful else self.env.get_name(obj)
        self.print_buf = []
        self.last_buf = []
        self.indent = len(objlst)

    def format(self) -> List[str]:
        # stkv = dfs_stk.pop()
        # stkv['it'].close()
        if not self.has_sth and not self.env.print_empty:
            return []
        lines = [self.name] + self.print_buf + indent_last(self.last_buf)
        if not self.has_sth and self.env.colorful:
            lines = [Ansi.faint(v) for v in lines]
        return lines

    def append_if_lines(self, lines: List[str], has_sth: bool) -> List[str]:
        self.has_sth |= has_sth
        if not lines:
            return []
        intermediate_lines, self.last_buf = \
            indent_intermediate(self.last_buf), lines
        self.print_buf.extend(intermediate_lines)
        return intermediate_lines


class Stack(Generic[T]):
    def __init__(self, env: StackEnv[T], root_obj: T):
        self.env = env
        self.dfs_stk = [StackNode(self.env, [], root_obj)]
        self.objlst = [v.obj for v in self.dfs_stk]

    def last(self) -> StackNode[T]:
        return self.dfs_stk[-1]

    def pop(self) -> StackNode[T]:
        self.objlst.pop()
        return self.dfs_stk.pop()

    def append(self, obj: T):
        self.dfs_stk.append(StackNode(self.env, self.objlst, obj))
        self.objlst.append(obj)

    def empty(self) -> bool:
        return len(self.dfs_stk) == 0

    def only_last_one(self) -> bool:
        return len(self.dfs_stk) == 1


class TreeFormatter(Generic[T]):
    """
    A
    ├── B
    │   └── D
    └── C
    A
    └──<found nothing>
    """

    def __init__(self,
                 get_name: Callable[[T], str],
                 get_iter: Callable[[List[T], T], Iterator[T]],
                 walk_cond: Callable[[List[T], T], bool],
                 print_cond: Callable[[List[T], T], bool],
                 *,
                 print_empty: bool = False,
                 colorful: bool = True):
        self.walk_cond = walk_cond
        self.print_cond = print_cond
        self.get_name = get_name
        self.get_iter = get_iter
        self.print_empty = print_empty
        self.colorful = colorful
        self.found_nothing_str: Final[str] = Ansi.faint('└──' + (
            Ansi.italic if self.colorful else lambda v: v)(
                '<found nothing>'))

    def walk_from_obj(self, root_obj: T, *, directly_call=True) \
            -> Generator[str, None, bool]:
        yield ((lambda v: Ansi.bold(Ansi.dircolor(v)))
               if self.colorful else lambda v: v)(
            self.get_name(root_obj))
        dfs_stk = Stack(
            StackEnv(self.get_iter, self.get_name,
                     self.print_empty, self.colorful),
            root_obj)
        while True:
            child_obj = next(dfs_stk.last().it, None)
            if child_obj is None:  # go up
                o = dfs_stk.pop()
                if dfs_stk.empty():
                    yield from indent_last(o.last_buf) \
                        or ([self.found_nothing_str] if directly_call else [])
                    return o.has_sth
                lines = dfs_stk.last().append_if_lines(o.format(), o.has_sth)
                if dfs_stk.only_last_one():
                    yield from lines
            elif self.walk_cond(dfs_stk.objlst, child_obj):  # go down
                dfs_stk.append(child_obj)
            elif self.print_cond(dfs_stk.objlst, child_obj):  # go next
                lines = dfs_stk.last().append_if_lines([
                    self.get_name(child_obj)], True)
                if dfs_stk.only_last_one():
                    yield from lines

    def walk_from_name(self, root_name: str, root_iter: Iterator[T]) \
            -> Iterator[str]:
        yield Ansi.bold(Ansi.dircolor(root_name)) \
            if self.colorful else root_name
        last_buf: List[str] = []
        has_sth: bool = False
        for obj in root_iter:
            lines: List[str] = []
            if self.walk_cond([], obj):
                it = self.walk_from_obj(obj, directly_call=False)
                e_has_sth: bool = False
                while True:
                    try:
                        lines.append(next(it))
                    except StopIteration as e:
                        e_has_sth = e.value
                        if not e_has_sth and self.colorful:
                            lines = [Ansi.faint(v) for v in lines]
                        has_sth |= e_has_sth
                        break
                if not e_has_sth and not self.print_empty:
                    continue
            elif self.print_cond([], obj):
                lines = [self.get_name(obj)]
                has_sth = True
            if len(lines) == 0:
                continue
            yield from indent_intermediate(last_buf)
            last_buf = lines
        yield from indent_last(last_buf) or [self.found_nothing_str]
