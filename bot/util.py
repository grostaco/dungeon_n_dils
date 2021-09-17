from discord_components import Interaction
from discord.ext import commands


async def remove_callback(inter: Interaction):
    await inter.edit_origin(delete_after=0)


async def start_wait(bot: commands.Bot, startable):
    await startable.start()
    await bot.wait_for('button_click', check=lambda inter: inter.custom_id == 'continue')
