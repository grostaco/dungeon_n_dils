from abc import ABCMeta, abstractmethod
from typing import List, Optional, Any

import discord
from discord.abc import Messageable
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    Interaction,
    Component,
)

from .util import remove_callback
import rpg


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

        return discord.Embed(title=self.select_title,
                             description=desc)

    async def start(self, inter: Optional[Interaction] = None):
        if inter:
            await inter.edit_origin(embed=self.get_embed(),
                                    components=self.get_components())
        else:
            await self.channel.send(embed=self.get_embed(),
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


class SkillSelect(Selectable):
    def __init__(self, client: DiscordComponents, channel: Messageable, skills: List[rpg.Skill]):
        super().__init__(client, channel, [skill.name for skill in skills], 'Skill select',
                         select_button=Button(label='Select', custom_id='skill_selected'))

    async def select_callback(self, _inter: Interaction): await remove_callback(_inter)


class TargetSelect(Selectable):
    def __init__(self, client: DiscordComponents, channel: Messageable, _fight: rpg.Fight):
        super().__init__(client, channel, [c.name for c in _fight.lookup], 'Select your target',
                         select_button=Button(label='Select', custom_id='target_selected'))

    async def select_callback(self, _inter: Interaction): await remove_callback(_inter)
