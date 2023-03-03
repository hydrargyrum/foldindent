#!/usr/bin/env python3

import argparse
import bisect
import sys
from dataclasses import dataclass, field

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree
from textual.widgets.tree import TreeNode


@dataclass
class Node:
    value: str
    children: list["Node"] = field(default_factory=list)


def _print_nodes(node, indent=0):
    print(indent * "  ", node.value)
    for c in node.children:
        print_nodes(c, indent + 1)


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

        new = Node(value=line)
        if indent == levels[-1]:
            objs[-2].children.append(new)
            objs[-1] = new
        elif indent > levels[-1]:
            objs[-1].children.append(new)
            objs.append(new)
            levels.append(indent)
        else:
            pos = levels.index(indent)
            del objs[pos:]
            del levels[pos:]

            objs[-1].children.append(new)
            objs.append(new)
            levels.append(indent)

    return ret


class FoldApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "exit", "quit"),
    ]

    def __init__(self, data):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Tree("root", id="tree")

    def action_exit(self):
        self.exit()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_mount(self):
        self.query_one("#tree").focus()
        self.feed(self.data)

    def search_hidden(self):
        self.query_one("#tree").focus()

    def feed(self, data: Node):
        tree = self.query_one(Tree)

        def recurse(tnode: TreeNode, dnode: Node):
            for sdnode in dnode.children:
                if sdnode.children:
                    stnode = tnode.add(sdnode.value)
                    recurse(stnode, sdnode)
                else:
                    tnode.add_leaf(sdnode.value)

        recurse(tree.root, data)
        tree.root.expand_all()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("file")
    args = argparser.parse_args()

    with open(args.file) as fp:
        text = fp.read()

    DATA = parse_indented(text)

    app = FoldApp(DATA)
    app.run()
