import json

from bot import DungeonBot

d = DungeonBot()
d.run(json.load(open('.env'))['token'])
