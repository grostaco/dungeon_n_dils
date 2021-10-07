from abc import ABCMeta, abstractmethod
from typing import List, Optional, Any, Iterable
from itertools import zip_longest

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
from rpg import Character, Effect, Skill, Fight


# noinspection PyArgumentList
class Selectable(metaclass=ABCMeta):
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 options: List[Any],
                 select_title: str,
                 up_button: Optional[Button] = Button(style=ButtonStyle.blue, emoji='🔼'),
                 down_button: Optional[Button] = Button(style=ButtonStyle.blue, emoji='🔽'),
                 select_button: Optional[Button] = Button(style=ButtonStyle.blue, label='Select'),
                 extra_components: List[Component] = None):
        self.client = client
        self.channel = channel
        self.options = options
        self.select_title = select_title
        self.up_button = up_button
        self.down_button = down_button
        self.select_button = select_button
        self.extra_components = extra_components or []
        self.index = 0
        self._component: Optional[ComponentMessage] = None

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
                     description=desc)

    async def start(self, inter: Optional[ComponentMessage] = None):
        if inter:
            await inter.edit(embed=self.get_embed(),
                             components=self.get_components())
        else:
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
    def __init__(self, client: DiscordComponents, channel: Messageable, skills: List[Skill]):
        super().__init__(client, channel, [skill.name for skill in skills], 'Skill select',
                         select_button=Button(label='Select', custom_id='skill_selected'))

    async def select_callback(self, _inter: Interaction): await respond_callback(_inter)


class TargetSelect(Selectable):
    def __init__(self, client: DiscordComponents, channel: Messageable, _fight: Fight):
        super().__init__(client, channel, [c.name for c in _fight.lookup], 'Select your target',
                         select_button=Button(label='Select', custom_id='target_selected'))

    async def select_callback(self, _inter: Interaction): await respond_callback(_inter)


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
                   f'{self.get_health_bar(lc) if lc.name else "": <16}'\
                   f'{self.get_health_bar(rc) if rc.name else "": >26}\n' \
                   f'{"Effects" if lc.name else "":<10} {"Effects" if rc.name else "":>26}'
            for l_effect, r_effect in zip_longest(lc.effects, rc.effects, fillvalue=None):
                l_effect_str = f'{l_effect.name} ({l_effect.duration} Turns)' if l_effect else ''
                r_effect_str = f'{r_effect.name} ({r_effect.duration} Turns)' if r_effect else ''
                buf += f'{l_effect_str:<30}{r_effect_str}\n'
            buf += '\n\n'
        buf += '```'
        return buf

    async def send(self):
        for character in self.fight.lookup:
            character.update_effective_stats()

        self.message = await self.channel.send(content=self.get_ui_text())

    async def update(self):
        await self.message.edit(content=self.get_ui_text())

    async def delete(self):
        await self.message.delete()
        self.message = None

