from typing import List, Optional, Sequence, Any, Callable
from abc import ABCMeta, abstractmethod
import rpg
import discord
from .util import remove_callback
import itertools

from discord.abc import Messageable
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    Interaction,
    Component,
)


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
        self.index = (self.index + 1) % len(self.options)
        await self.button_callback(inter)

    async def button_down_callback(self, inter: Interaction):
        self.index = (self.index - 1) % len(self.options)
        await self.button_callback(inter)

    @abstractmethod
    async def select_callback(self, inter: Interaction):
        ...

    async def button_callback(self, inter: Interaction):
        await inter.edit_origin(embed=self.get_embed(),
                                components=self.get_components())


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

    # noinspection PyArgumentList
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


class Choice(Selectable):
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 choice: rpg.Choice,
                 select_title: str = 'You are presented with a choice!'):
        super().__init__(client, channel, [dialogue[0] for dialogue in choice], select_title,
                         select_button=Button(label='Continue'))
        self.choice = choice

    async def select_callback(self, inter: Interaction):
        await remove_callback(inter)
        await Dialogue(client=self.client, channel=self.channel,
                       dialogue=self.choice[self.index][1]).start()


class Fight:
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 party_one: List[rpg.Player],
                 party_two: List[rpg.Character]):
        self.client = client
        self.channel = channel
        self.party_one = party_one
        self.party_two = party_two
        self.original_message = None

        self.inventory = Inventory(client, channel, party_one, self.update)

    def get_embed(self):
        embed = discord.Embed(title='It\'s showtime!')
        fill_char = '      VS      '
        for p1, p2 in itertools.zip_longest(self.party_one, self.party_two,
                                            fillvalue=rpg.Character('\u200b')):
            def stat_str(character):
                if character.name == '\u200b':
                    return '\u200b'
                else:
                    stats = character.get_item_stats()
                    return f'hp: {character.stats.hp} (+{stats.hp})\n' \
                           f'atk: {character.stats.atk} (+{stats.atk})\n' \
                           f'def: {character.stats.defense} (+{stats.defense})\n' \
                           f'int: {character.stats.int} (+{stats.int})'

            embed.add_field(name=p1.name, value=stat_str(p1), inline=True)
            embed.add_field(name=fill_char, value='\u200b')
            embed.add_field(name=p2.name, value=stat_str(p2), inline=True)
            fill_char = '\u200b'

        return embed

    async def open_inventory(self, inter: Interaction):
        await inter.edit_origin(embed=self.get_embed())
        await self.inventory.start()

    async def update(self):
        await self.original_message.edit(embed=self.get_embed())

    async def start(self):
        # noinspection PyArgumentList
        self.original_message = await self.channel.send(embed=self.get_embed(),
                                                        components=[[
                                                            self.client.add_callback(
                                                                Button(style=ButtonStyle.blue, label='Proceed',
                                                                       custom_id='sub_continue'),
                                                                remove_callback
                                                            ),
                                                            Button(style=ButtonStyle.green, label='Shops',
                                                                   disabled=True),
                                                            self.client.add_callback(
                                                                Button(style=ButtonStyle.green, label='Inventory'),
                                                                self.open_inventory
                                                            )
                                                        ]])

        await self.client.bot.wait_for('button_click', check=lambda inter: inter.custom_id == 'sub_continue')


class Inventory(Selectable):
    def __init__(self,
                 client: DiscordComponents,
                 channel: Messageable,
                 players: List[rpg.Player],
                 update_fn: Callable):
        super().__init__(client, channel, [player.name for player in players], 'Whose inventory do you want to view?',
                         select_button=Button(label='View', custom_id='view'),
                         extra_components=[client.add_callback(Button(style=ButtonStyle.red, label='Back'),
                                                               remove_callback)])
        self.client = client
        self.channel = channel
        self.players = players
        self.last_chosen = 'weapons'
        self.update_fn = update_fn

    async def select_callback(self, inter: Interaction):
        if inter.custom_id not in {'weapons', 'armors', 'consumables'}:
            inter.custom_id = 'weapons'
        prop = inter.custom_id
        self.last_chosen = inter.custom_id
        player = self.players[self.index]
        embed = discord.Embed(title=f'{player.name}\'s inventory',
                              description='\n\n'.join(
                                  f'{item.name}\n*{item.flavor_text}*' for item in getattr(player, prop)))
        styles = [ButtonStyle.green] * 3
        styles[{'weapons': 0, 'armors': 1, 'consumables': 2}[inter.custom_id]] = ButtonStyle.gray
        await inter.edit_origin(embed=embed,
                                components=self.get_inventory_components(style_array=styles))

    async def view_selection(self, inter: Interaction):
        await inter.edit_origin(embed=Selectable.get_embed(self),
                                components=Selectable.get_components(self))

    async def equip_callback(self, inter: Interaction):
        if self.last_chosen == 'consumables':
            await inter.respond(type=7)
            return

        class InventoryEquip(Selectable):
            def __init__(self, inv: Inventory):
                super().__init__(inv.client, inv.channel,
                                 getattr(inv.players[inv.index], inv.last_chosen),
                                 select_title=f'{inv.players[inv.index].name}\'s {inv.last_chosen}',
                                 select_button=Button(label='Equip', custom_id='equip',
                                                      style=ButtonStyle.blue),
                                 extra_components=[
                                     inv.client.add_callback(Button(label='Unequip', custom_id='unequip',
                                                                    style=ButtonStyle.blue),
                                                             self.select_callback),
                                     inv.client.add_callback(Button(label='Back', style=ButtonStyle.red),
                                                             inv.select_callback)])
                self.last_option = 0
                self.inv = inv
                self.player = self.inv.players[self.inv.index]
                self.target_inv = getattr(inv.players[inv.index], inv.last_chosen)

            def get_embed(self):
                desc = ''
                for i, option in enumerate(self.options):
                    if i == self.index:
                        desc += '▶️   '
                    desc += f'{option.name}\n'

                return discord.Embed(title=self.select_title,
                                     description=desc)

            async def select_callback(self, _inter: Interaction):
                if _inter.custom_id == 'equip':
                    if self.inv.last_chosen == 'weapons':
                        self.player.equip_weapon(self.options[self.index])
                    else:
                        self.player.equip_armor(self.options[self.index])
                else:
                    if self.inv.last_chosen == 'weapons':
                        self.player.unequip_weapon()
                    else:
                        self.player.unequip_armor(self.options[self.index])

                await self.inv.update_fn()
                await _inter.edit_origin(embed=self.get_embed(), components=self.get_components())

        await InventoryEquip(self).start(inter)

    def get_inventory_components(self, *, style_array: Sequence[ButtonStyle] = (ButtonStyle.green,) * 3):
        return [
            [
                self.client.add_callback(
                    Button(style=style_array[0], label='Weapons', custom_id='weapons'),
                    self.select_callback,
                ),
                self.client.add_callback(
                    Button(style=style_array[1], label='Armor', custom_id='armors'),
                    self.select_callback,
                ),
                self.client.add_callback(
                    Button(style=style_array[2], label='Consumables', custom_id='consumables'),
                    self.select_callback,
                ),
                self.client.add_callback(
                    Button(style=ButtonStyle.blue, label='Equip', custom_id='equip'),
                    self.equip_callback,
                ),
                self.client.add_callback(
                    Button(style=ButtonStyle.red, label='Back'),
                    self.view_selection,
                )
            ]
        ]
