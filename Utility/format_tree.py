from typing import List, Iterator, Callable, TypeVar, Generic, Final

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
                 print_empty: bool):
        self.get_iter = get_iter
        self.get_name = get_name
        self.print_empty = print_empty


class StackNode(Generic[T]):
    def __init__(self, env: StackEnv[T], objlst: List[T], obj: T):
        self.env = env
        self.obj = obj
        self.it = self.env.get_iter(objlst, obj)
        self.has_sth = False
        self.print_buf = [self.env.get_name(obj)]
        self.last_buf = []
        self.indent = len(objlst)

    def format(self) -> List[str]:
        # stkv = dfs_stk.pop()
        # stkv['it'].close()
        if self.has_sth or self.env.print_empty:
            return self.print_buf + indent_last(self.last_buf)
        return []

    def append_if_lines(self, lines: List[str]) -> List[str]:
        if not lines:
            return []
        intermediate_lines, self.last_buf = \
            indent_intermediate(self.last_buf), lines
        self.print_buf.extend(intermediate_lines)
        self.has_sth = True
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

    found_nothing_str: Final[str] = '└──<found nothing>'

    def __init__(self,
                 get_name: Callable[[T], str],
                 get_iter: Callable[[List[T], T], Iterator[T]],
                 walk_cond: Callable[[List[T], T], bool],
                 print_cond: Callable[[List[T], T], bool],
                 *, print_empty: bool = False):
        self.walk_cond = walk_cond
        self.print_cond = print_cond
        self.get_name = get_name
        self.get_iter = get_iter
        self.print_empty = print_empty
        # self.env = StackEnv[T](get_iter, get_name, print_empty)

    def walk_from_obj(self, root_obj: T) -> Iterator[str]:
        yield self.get_name(root_obj)
        dfs_stk = Stack(
            StackEnv(self.get_iter, self.get_name, self.print_empty),
            root_obj)
        while True:
            child_obj = next(dfs_stk.last().it, None)
            if child_obj is None:  # go up
                o = dfs_stk.pop()
                if dfs_stk.empty():
                    yield from indent_last(o.last_buf) \
                        or [self.found_nothing_str]
                    return
                lines = dfs_stk.last().append_if_lines(o.format())
                if dfs_stk.only_last_one():
                    yield from lines
            elif self.walk_cond(dfs_stk.objlst, child_obj):  # go down
                dfs_stk.append(child_obj)
            elif self.print_cond(dfs_stk.objlst, child_obj):  # go next
                lines = dfs_stk.last().append_if_lines([
                    self.get_name(child_obj)])
                if dfs_stk.only_last_one():
                    yield from lines

    def walk_from_name(self, root_name: str, root_iter: Iterator[T]) \
            -> Iterator[str]:
        yield root_name
        last_buf: List[str] = []
        for obj in root_iter:
            lines: List[str] = []
            if self.walk_cond([], obj):
                lines = list(self.walk_from_obj(obj))
            elif self.print_cond([], obj):
                lines = [self.get_name(obj)]
            if len(lines) == 0 or lines[-1] == self.found_nothing_str:
                continue
            yield from indent_intermediate(last_buf)
            last_buf = lines
        yield from indent_last(last_buf) or [self.found_nothing_str]
