from notion_auto_organizer.notion import NotionClient


class FakeNotionClient(NotionClient):
    def __init__(self):
        self.appended = []

    def append_children(self, block_id, children):
        for start in range(0, len(children), 100):
            self.appended.append(children[start : start + 100])


def test_append_children_chunks_at_100():
    client = FakeNotionClient()
    blocks = [{"object": "block", "type": "divider", "divider": {}} for _ in range(205)]

    client.append_children("page", blocks)

    assert [len(chunk) for chunk in client.appended] == [100, 100, 5]
