import discord
from discord_components import ComponentsBot

import rpg
from .ui import Fight, Dialogue, Choice
from .util import start_wait


class DungeonBot(ComponentsBot):
    def __init__(self):
        super().__init__(';')

    async def on_ready(self):
        beginning = rpg.Dialogue()
        najim = rpg.Player('Najim', [rpg.Weapon('MILF hunter sword', 'A sentient sword that likes milfs',
                                                rpg.Stats(atk=16)),
                                     rpg.Weapon('Faulty Calculator', 'Adds +1 int, but only if the user knows how '
                                                                     'to operate calculators', rpg.Stats())],
                           [rpg.Consumable('Dildo', 'A regular dildo'),
                            rpg.Consumable('Fleshlight', 'A regular fleshlight')],
                           [rpg.Armor('Fortnite shoes', 'Shoes that spreads cancer with every step', 1,
                                      rpg.Stats(hp=69)),
                            rpg.Armor('Yeezy (singular) ', 'The long lost pair of roar\'s yeezy',
                                      1, rpg.Stats(hp=32, defense=5))],
                           rpg.Stats(0, 16, 0, 0))
        roar = rpg.Player('RoaR', [rpg.Weapon('A fish', '', rpg.Stats())],
                          [rpg.Consumable('Bomb', '')],
                          [rpg.Armor('Yeezy', 'Overpriced shoe(singular)', 1, rpg.Stats())]
                          , rpg.Stats(32, 16, 16, 5))
        chicken = rpg.Character('Chicken God', [], [], [], rpg.Stats(16, 1, 1, 64))
        chn: discord.TextChannel = self.get_channel(887345509990285315)

        najim.equip_weapon('MILF hunter sword')
        najim.equip_armor('Fortnite shoes')

        fight = Fight(self.components_manager,
                      chn,
                      [najim, roar],
                      [chicken])

        beginning.add_line(chicken, 'Let me suck your pp')

        await start_wait(self, Dialogue(self.components_manager, chn, beginning))

        bc = rpg.Choice()
        bc.add_choice('No', rpg.Dialogue([(najim, 'No'), (roar, 'Weirdo no'), (chicken, 'Too bad')]))
        bc.add_choice('Ew no fag', rpg.Dialogue([(najim, 'Faggots'), (chicken, 'Alright faggot, bring it on')]))

        await start_wait(self, Choice(self.components_manager, chn, bc))

        await fight.start()
