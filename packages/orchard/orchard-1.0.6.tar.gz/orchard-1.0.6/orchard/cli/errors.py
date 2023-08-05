from textwrap import dedent


class UserError(Exception):
    def __init__(self, msg):
        self.msg = dedent(msg).strip()
