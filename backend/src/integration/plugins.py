from backend.src.integration import Plugin

import typing as t


class OnlineTextPlugin(Plugin):
    type: t.ClassVar[str] = 'onlinetext'

    def handle(self) -> t.Any:
        # TODO: add onlinetext handler
        return


class FilePlugin(Plugin):
    type: t.ClassVar[str] = 'file'

    def handle(self) -> t.Any:
        # TODO: add file handler
        return


class CommentsPlugin(Plugin):
    type: t.ClassVar[str] = 'comments'

    def handle(self) -> t.Any:
        # TODO: add comments handler
        return
