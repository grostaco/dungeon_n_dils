from .script import Script, Dialogue, Choice


# Script
# -> characters
# -> script
# -> state


class World:
    def __init__(self, script: Script):
        self.script = iter(script)

    def advance(self):
        act = next(self.script)
