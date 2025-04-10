
import pytest

import foldindent


DATA = foldindent.Node(
    "", [
        foldindent.Node("nope", []),
        foldindent.Node("big", [
            foldindent.Node("some", [
                foldindent.Node("end", []),
            ]),
            foldindent.Node("small", []),
        ]),
    ]
)


@pytest.mark.asyncio
async def test_buttons():
    app = foldindent.FoldApp(DATA)
    async with app.run_test() as pilot:
        tree = app.get_child_by_id("tree")

        for expected in ("root", "nope", "big", "some", "end", "small"):
            assert tree.cursor_node.label.plain == expected
            await pilot.press("down")

        assert len(tree.root.children) == 2
        assert tree.root.children[1].children[0].label.plain == "some"
        # await pilot.click("#red")
