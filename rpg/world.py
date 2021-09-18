from .script import Script


# Script
# -> characters
# -> script
# -> state


class World:
    def __init__(self, script: Script):
        self.script = iter(script)

    def advance(self):
        ...
