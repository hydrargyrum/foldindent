import bisect
import sys
import json
from dataclasses import dataclass, field

from textual.widgets.tree import TreeNode
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree


@dataclass
class Node:
    value: str
    children: list = field(default_factory=list)


def parse_indented(text):
    ret = Node(value="")
    objs = [ret]
    levels = [-1]

    lines = text.split("\n")
    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        line = line.strip()

        if indent == levels[-1]:
            objs[-2].children.append(Node(value=line))
        elif indent > levels[-1]:
            new = Node(value=line)
            objs[-1].children.append(new)
            objs.append(new)
            levels.append(indent)
        else:
            pos = levels.index(indent)
            del objs[pos:]
            del levels[pos:]

            new = Node(value=line)
            objs[-1].children.append(new)
            objs.append(new)
            levels.append(indent)

            continue
            pos = bisect.bisect(levels, indent)
            objs[-1].children.append(Node(value=line))
    return ret


class FoldApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "exit", "quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Tree("root")

    def action_exit(self):
        self.exit()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_mount(self):
        self.feed(DATA)
        print(self.feed)

    def feed(self, data):
        tree = self.query_one(Tree)

        def leaf_or_recurse(node, k, obj):
            if isinstance(obj, (int, bool, str, float, type(None))):
                node.add_leaf(str(obj))
            else:
                sub = node.add(str(k))
                recurse(sub, obj)

        def recurse(treenode, obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    sub = treenode.add(k)
                    recurse(sub, v)
                return
            elif isinstance(obj, list):
                for n, v in enumerate(obj):
                    #sub = treenode.add(str(n))
                    #recurse(sub, v)
                    leaf_or_recurse(treenode, n, v)
                return
            elif isinstance(obj, (int, bool, str, float, type(None))):
                treenode.add_leaf(str(obj))
                return
            raise NotImplementedError(type(obj))

        recurse(tree.root, data)
        tree.root.expand_all()

    def feed(self, data):
        tree = self.query_one(Tree)

        def recurse(tnode, dnode):
            for sdnode in dnode.children:
                if True or sdnode.children:
                    stnode = tnode.add(sdnode.value)
                    recurse(stnode, sdnode)
                else:
                    tnode.add_leaf(sdnode.value)

        recurse(tree.root, data)
        tree.root.expand_all()


if __name__ == "__main__":
    with open(sys.argv[1]) as fp:
#            self.feed(json.load(fp))
        DATA = parse_indented(fp.read())
        print(DATA)

    app = FoldApp()
    app.run()
