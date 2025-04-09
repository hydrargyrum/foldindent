
import pytest

from foldindent import Node, parse_indented


TEXT = """
foo
    bar
        baz
    qux
quack
"""

NODES = Node(
    "", [
        Node(
            "foo", [
                Node(
                    "bar", [
                        Node("baz", []),
                    ]
                ),
                Node("qux", []),
            ]
        ),
        Node("quack", []),
    ]
)


@pytest.mark.parametrize("text, expected", [
    (TEXT, NODES),
])
def test_parse(text, expected):
    got = parse_indented(text)
    assert got == expected
