from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Optional, Any, Union, Tuple, TYPE_CHECKING
from itertools import zip_longest
from asyncio.futures import Future

from discord.abc import Messageable
from discord import Message, Embed
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    Interaction,
    Component,
    ComponentMessage,
)

from .util import remove_callback, respond_callback
from rpg import Weapon, Armor, Consumable, Character

if TYPE_CHECKING:
    from rpg import Skill, Fight, Item


# noinspection PyArgumentList
class Selectable(metaclass=ABCMeta):
    def __init__(self,
                 client: DiscordComponents,
                 channel: Optional[Messageable],
                 options: List[Any],
                 select_title: str,
                 up_button: Optional[Button] = None,
                 down_button: Optional[Button] = None,
                 select_button: Optional[Button] = None,
                 extra_components: List[Component] = None,
                 color: Optional[int] = 0):
        self.client = client
        self.channel = channel
        self.options = options
        self.select_title = select_title
        self.up_button = up_button or Button(style=ButtonStyle.blue, emoji='🔼')
        self.down_button = down_button or Button(style=ButtonStyle.blue, emoji='🔽')
        self.select_button = select_button or Button(style=ButtonStyle.blue, label='Select')
        self.extra_components = extra_components or []
        self.index = 0
        self._component: Optional[ComponentMessage] = None
        self.color = color

    def get_components(self):
        return [
            [
                self.client.add_callback(
                    self.up_button,
                    self.button_up_callback,
                ),
                self.client.add_callback(
                    self.down_button,
                    self.button_down_callback,
                ),
                self.client.add_callback(
                    self.select_button,
                    self.select_callback,
                ),
            ] + self.extra_components
        ]

    def get_embed(self):
        desc = ''
        for i, option in enumerate(self.options):
            if i == self.index:
                desc += '▶️   '
            desc += f'{option}\n'

        return Embed(title=self.select_title,
                     description=desc, color=self.color)

    async def start(self, inter_or_comp: Optional[Union[ComponentMessage, Interaction]] = None):
        if isinstance(inter_or_comp, Interaction):
            await inter_or_comp.edit_origin(embed=self.get_embed(),
                                            components=self.get_components())
        elif isinstance(inter_or_comp, ComponentMessage):
            await inter_or_comp.edit(embed=self.get_embed(),
                                     components=self.get_components())
        else:
            if not self.channel:
                raise ValueError('Channel cannot be None if inter_or_comp is not supplied')
            self._component = await self.channel.send(embed=self.get_embed(),
                                                      components=self.get_components())

    async def button_up_callback(self, inter: Interaction):
        self.index = (self.index - 1) % len(self.options)
        await self.button_callback(inter)

    async def button_down_callback(self, inter: Interaction):
        self.index = (self.index + 1) % len(self.options)
        await self.button_callback(inter)

    @abstractmethod
    async def select_callback(self, inter: Interaction):
        ...

    async def button_callback(self, inter: Interaction):
        await inter.edit_origin(embed=self.get_embed(),
                                components=self.get_components())

    @property
    def component(self):
        return self._component


class SkillSelect(Selectable):
    def __init__(self, client: DiscordComponents, channel: Messageable, skills: List[Skill],
                 player_name: str):
        super().__init__(client, channel, [skill.name for skill in skills],
                         f'{player_name}\'s turn, select your skill!',
                         color=0xBC544B)
        self.exited: Future[bool] = self.create_future()

    def create_future(self):
        return self.client.bot.loop.create_future()

    async def select_callback(self, inter: Interaction):
        await respond_callback(inter)
        if self.exited.done():
            self.exited = self.create_future()

        self.exited.set_result(True)


class TargetSelect(Selectable):
    def __init__(self, client: DiscordComponents, channel: Messageable, _fight: Fight):
        super().__init__(client, channel, [c.name for c in _fight.lookup], 'Select your target',
                         color=0xFFC9AD)
        self.exited: Future[bool] = self.create_future()

    def create_future(self):
        return self.client.bot.loop.create_future()

    async def select_callback(self, inter: Interaction):
        await respond_callback(inter)
        if self.exited.done():
            self.exited = self.create_future()

        self.exited.set_result(True)


class FightUI:
    def __init__(self, channel: Messageable, fight: Fight):
        self.channel = channel
        self.fight = fight
        self.message: Optional[Message] = None

    def get_ui_text(self):
        buf = '```swift\n'
        t = iter((f'{"VS"}',))
        for lc, rc in zip_longest(self.fight.left, self.fight.right, fillvalue=Character('')):
            buf += f'{lc.name:<12}{next(t, ""):^18}{rc.name}\n' \
                   f'{self.get_health_bar(lc) if lc.name else "": <16}' \
                   f'{self.get_health_bar(rc) if rc.name else "": >26}\n' \
                   f'{"Effects" if lc.name else "":<10} {"Effects" if rc.name else "":>26}'
            for l_effect, r_effect in zip_longest(lc.effects, rc.effects, fillvalue=None):
                buf += '\n'
                l_effect_str = f'{l_effect.name} ({l_effect.duration} Turns)' if l_effect else ''
                r_effect_str = f'{r_effect.name} ({r_effect.duration} Turns)' if r_effect else ''
                buf += f'{l_effect_str:<30}{r_effect_str}'
            buf += '\n\n'
        buf += '```'
        return buf

    async def send(self):
        for character in self.fight.lookup:
            character.update_effective_stats()

        self.message = await self.channel.send(content=self.get_ui_text())

    async def update(self):
        await self.message.edit(content=self.get_ui_text())

    async def remove(self):
        await self.message.delete()
        self.message = None

    @staticmethod
    def get_health_bar(character: Character):
        return "[" + "#" * int(character.effective_stats.hp / character.stats.hp * 10) + \
               "-" * (10 - int(character.effective_stats.hp / character.stats.hp * 10)) + "]"


class CombatLog:
    def __init__(self, channel: Messageable):
        self.logs: List[str] = []
        self.channel = channel
        self.message: Optional[Message] = None

    def get_embed(self) -> Embed:
        embed = Embed(title='Combat Log', color=0x63C5DA)
        embed.description = '\n'.join(self.logs)
        if len(embed.description) >= 4096:
            self.logs = ['---------- Truncated ----------']
            embed.description = '\n'.join(self.logs)
        return embed

    async def send(self):
        self.message = await self.channel.send(embed=self.get_embed())

    async def update(self):
        await self.message.edit(embed=self.get_embed())

    def clear_log(self):
        self.logs.clear()

    def add_log(self, message: str):
        self.logs.append(message)

    async def remove(self):
        await self.message.delete()


class Shop(Selectable):
    def __init__(self, client: DiscordComponents, channel: Messageable,
                 catalogue: List[Tuple[Item, int]], players: List[Character],
                 balance: int):
        super().__init__(client, channel, [x[0].name for x in catalogue],
                         'Shop Selection')
        self.catalogue = catalogue
        self.extra_components = self.get_extra_components()
        self.players = players
        self.balance = balance
        self.exited: Future[bool] = self.client.bot.loop.create_future()

    def get_extra_components(self, disabled: bool = False):
        return [
            self.client.add_callback(
                Button(label='Exit', style=ButtonStyle.red, disabled=disabled),
                self.on_exit,
            )
        ]

    async def on_exit(self, inter: Interaction):
        await remove_callback(inter)
        self.exited.set_result(True)

    async def select_callback(self, inter: Interaction):
        await inter.edit_origin(components=self.get_components())
        sd = ShopDesc(self.client, self.catalogue[self.index], [player.name for player in self.players])
        await sd.start(inter)
        choice = await sd.promise

        if choice != -1:
            item, price = self.catalogue[self.index]
            player = self.players[choice]
            if self.balance >= price:
                if isinstance(item, Weapon):
                    if item.name not in (weapon.name for weapon in player.weapons):
                        player.weapons.append(item)
                        self.balance -= price
                elif isinstance(item, Armor):
                    if item.name not in (armor.name for armor in player.armors):
                        self.balance -= price
                        player.armors.append(item)
                elif isinstance(item, Consumable):
                    player.consumables.append(item)
                    self.balance -= price

        await inter.message.edit(embed=self.get_embed(), components=self.get_components())


class ShopDesc:
    def __init__(self, client: DiscordComponents, catalogue_info: Tuple[Item, int], players: List[str]):
        self.client = client
        self.catalogue_info = catalogue_info
        self.players = players
        self.promise: Future[int] = self.client.bot.loop.create_future()

    def get_components(self):
        return [
            [
                self.client.add_callback(
                    Button(
                        label='Buy',
                        style=ButtonStyle.green,
                    ),
                    self.buy,
                ),
                self.client.add_callback(
                    Button(
                        label='Back',
                        style=ButtonStyle.red,
                    ),
                    self.done,
                )
            ]
        ]

    def get_embed(self) -> Embed:
        embed = Embed(title='Item inspection screen')
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/839838748413788200/898425885391224832/unknown.png')
        embed.add_field(name='**__Item name__**', value=self.catalogue_info[0].name)
        embed.add_field(name='**__Price__**', value=f'{self.catalogue_info[1]} shidcoins')
        embed.add_field(name='\u200b', value='\u200b')
        embed.add_field(name='**__Description__**', value=f'*{self.catalogue_info[0].flavor_text}*')
        return embed

    async def buy(self, inter: Interaction):
        player_select = SimpleSelect(self.client, None, self.players, 'Selection')
        await player_select.start(inter)
        self.promise.set_result(await player_select.selection)
        await respond_callback(inter)

    async def done(self, inter: Interaction):
        self.promise.set_result(-1)
        await respond_callback(inter)

    async def start(self, inter: Interaction):
        await inter.message.edit(embed=self.get_embed(), components=self.get_components())


class SimpleSelect(Selectable):
    def __init__(self, client: DiscordComponents, channel: Optional[Messageable], options: List[str],
                 title: str):
        super().__init__(client, channel, options, title, extra_components=[
            client.add_callback(
                Button(
                    label='Back',
                    style=ButtonStyle.red,
                ),
                self.select_callback,
            )
        ])
        self.selection: Future[int] = self.client.bot.loop.create_future()

    async def select_callback(self, inter: Interaction):
        await inter.respond(type=6)
        if inter.custom_id == 'back':
            self.selection.set_result(self.index)
            await remove_callback(inter)
        self.selection.set_result(self.index)
