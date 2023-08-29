#!/usr/bin/env python3
# SPDX-License-Identifier: WTFPL

import argparse
import bisect
import sys
from dataclasses import dataclass, field

from textual.app import App, ComposeResult
from textual.keys import Keys
from textual.widgets import Footer, Tree as _Tree
from textual.widgets.tree import TreeNode

__version__ = "0.3.0"


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

        pos = bisect.bisect_left(levels, indent)
        del objs[pos:]
        del levels[pos:]

        objs[-1].children.append(new)
        objs.append(new)
        levels.append(indent)

    return ret


class Tree(_Tree):
    BINDINGS = [
        ("^", "go_to_parent", "Parent"),
        (Keys.Left, "fold_current", "Parent"),
        (Keys.Right, "expand_current", "Expand"),
    ]

    def action_go_to_parent(self):
        self.select_node(self.cursor_node.parent)
        self.scroll_to_node(self.cursor_node)

    def action_fold_current(self):
        if self.cursor_node.children and self.cursor_node.is_expanded:
            self.cursor_node.collapse()
        else:
            self.select_node(self.cursor_node.parent)
            self.scroll_to_node(self.cursor_node)

    def action_expand_current(self):
        if not self.cursor_node.children:
            return

        if self.cursor_node.is_expanded:
            self.select_node(self.cursor_node.children[0])
            self.scroll_to_node(self.cursor_node)
        else:
            self.cursor_node.expand()


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


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("file")
    args = argparser.parse_args()

    with open(args.file) as fp:
        text = fp.read()

    DATA = parse_indented(text)

    app = FoldApp(DATA)
    app.run()


if __name__ == "__main__":
    main()
