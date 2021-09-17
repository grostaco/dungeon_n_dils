from typing import List
import rpg
import discord
from .util import remove_callback
import itertools

from discord.abc import Messageable
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    Interaction
)


class Dialogue:
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 dialogue: rpg.Dialogue):
        self.client = client
        self.channel = channel
        self.dialogue = dialogue
        self.no_skip = True
        self.index = 0

    def get_components(self):
        return [
            [
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, emoji="◀️"),
                    self.button_left_callback,
                ),
                Button(
                    label=f'Page {self.index + 1}/{len(self.dialogue)}',
                    disabled=True,
                ),
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, emoji="▶️"),
                    self.button_right_callback,
                ),
                self.client.add_callback(
                    Button(
                        label='Continue',
                        custom_id='continue',
                        disabled=self.no_skip,
                    ),
                    remove_callback
                )
            ]
        ]

    async def start(self):
        if len(self.dialogue) == 1:
            self.no_skip = False
        dialogue = self.dialogue[self.index]
        embed = discord.Embed(title=dialogue[0].name, description=dialogue[1])
        await self.channel.send(
            embed=embed, components=self.get_components()
        )

    async def button_left_callback(self, inter: Interaction):
        self.index = (self.index - 1) % len(self.dialogue)
        await self.button_callback(inter)

    async def button_right_callback(self, inter: Interaction):
        self.index = (self.index + 1) % len(self.dialogue)
        await self.button_callback(inter)

    async def button_callback(self, inter: Interaction):
        if self.index == len(self.dialogue) - 1:
            self.no_skip = False
        dialogue = self.dialogue[self.index]

        embed = discord.Embed(title=dialogue[0].name, description=dialogue[1])
        await inter.edit_origin(
            embed=embed, components=self.get_components()
        )


class Choice:
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 choice: rpg.Choice):
        self.client = client
        self.channel = channel
        self.choice = choice
        self.index = 0

    def get_components(self):
        return [
            [
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, emoji='🔼'),
                    self.button_up_callback,
                ),
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, emoji='🔽'),
                    self.button_down_callback,
                ),
                self.client.add_callback(
                    Button(label='Continue'),
                    self.continue_callback,
                )
            ]
        ]

    async def button_up_callback(self, inter: Interaction):
        self.index = (self.index - 1) % len(self.choice)
        await self.button_callback(inter)

    async def button_down_callback(self, inter: Interaction):
        self.index = (self.index + 1) % len(self.choice)
        await self.button_callback(inter)

    def get_description(self):
        desc = ''
        for i, choice in enumerate(self.choice):
            if i == self.index:
                desc += '▶️   '
            desc += f'{choice[0]}\n'
        return desc

    async def start(self, title='You are presented with a choice!'):
        await self.channel.send(embed=discord.Embed(title=title,
                                                    description=self.get_description()),
                                components=self.get_components())

    async def button_callback(self, inter: Interaction):
        await inter.edit_origin(embed=discord.Embed(title='You are presented with a choice!',
                                                    description=self.get_description()),
                                components=self.get_components())

    async def continue_callback(self, inter: Interaction):
        await remove_callback(inter)
        await Dialogue(client=self.client, channel=self.channel,
                       dialogue=self.choice[self.index][1]).start()


class Fight:
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 party_one: List[rpg.Character],
                 party_two: List[rpg.Character]):
        self.client = client
        self.channel = channel
        self.party_one = party_one
        self.party_two = party_two

    #        self.inventory = Inventory(client, channel, )

    def get_embed(self):
        embed = discord.Embed(title='It\'s showtime!')
        fill_char = '      VS      '
        for p1, p2 in itertools.zip_longest(self.party_one, self.party_two,
                                            fillvalue=rpg.Character('\u200b')):
            def stat_str(character):
                if character.name == '\u200b':
                    return '\u200b'
                else:
                    return f'hp: {character.stats.hp}\natk: {character.stats.atk}\n' \
                           f'def: {character.stats.defense}\nint: {character.stats.int}'

            embed.add_field(name=p1.name, value=stat_str(p1), inline=True)
            embed.add_field(name=fill_char, value='\u200b')
            embed.add_field(name=p2.name, value=stat_str(p2), inline=True)
            fill_char = '\u200b'

        return embed

    async def start(self):
        await self.channel.send(embed=self.get_embed(),
                                components=[[
                                    self.client.add_callback(
                                        Button(style=ButtonStyle.blue, label='Proceed',
                                               custom_id='sub_continue'),
                                        remove_callback
                                    ),
                                    Button(style=ButtonStyle.green, label='Shops', disabled=True),
                                    Button(style=ButtonStyle.green, label='Inventory', disabled=True),
                                ]])

        await self.client.bot.wait_for('button_click', check=lambda inter: inter.custom_id == 'sub_continue')


class Inventory:
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 players: List[rpg.Player]):
        self.client = client
        self.channel = channel
        self.players = players
        self.player_select_index = 0

    def get_select_embed(self):
        desc = ''
        for i, player in enumerate(self.players):
            if i == self.player_select_index:
                desc += '▶️   '
            desc += f'{player.name}\n'

        return discord.Embed(title='Whose inventory do you want to view?',
                             description=desc)

    async def button_up_callback(self, inter: Interaction):
        self.player_select_index = (self.player_select_index + 1) % len(self.players)
        await self.button_callback(inter)

    async def button_down_callback(self, inter: Interaction):
        self.player_select_index = (self.player_select_index - 1) % len(self.players)
        await self.button_callback(inter)

    async def button_callback(self, inter: Interaction):
        await inter.edit_origin(embed=self.get_select_embed())

    def get_select_components(self):
        return [
            [
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, emoji='🔼'),
                    self.button_up_callback,
                ),
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, emoji='🔽'),
                    self.button_down_callback,
                ),
                self.client.add_callback(
                    Button(label='View'),
                    None
                )
            ]
        ]

    async def start(self):
        await self.channel.send(embed=self.get_select_embed(), )
