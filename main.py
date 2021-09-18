from bot import DungeonBot
import json

d = DungeonBot()
d.run(json.load(open('.env'))['token'])
