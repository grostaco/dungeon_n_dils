from discord_components import ComponentsBot
import discord
from .ui import Dialogue, Choice, Fight
from .util import start_wait
import rpg


class DungeonBot(ComponentsBot):
    def __init__(self):
        super().__init__(';')

    async def on_ready(self):
        beginning = rpg.Dialogue()
        najim = rpg.Player('Najim', [rpg.Weapon('MILF hunter sword', '')], [rpg.Consumable('Dildo', '')],
                                    [rpg.Armor('Fortnite shoes', '', 1)], rpg.Stats(32, 16, 16, 0))
        roar = rpg.Player('RoaR', [rpg.Weapon('A fish', '')], [rpg.Consumable('Bomb', '')],
                                  [rpg.Armor('Yeezy', '', 1)], rpg.Stats(32, 16, 16, 5))
        chicken = rpg.Character('Chicken God', [], [], [], rpg.Stats(16, 1, 1, 64))
        chn: discord.TextChannel = self.get_channel(887345509990285315)

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
