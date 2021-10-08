from typing import Protocol, Callable, Optional, Any

from discord_components import Interaction


class Startable(Protocol):
    start: Callable


class Waitable(Protocol):
    wait_for: Callable


async def remove_callback(inter: Interaction):
    await inter.edit_origin(delete_after=0)


async def respond_callback(inter: Interaction, _type: int = 7):
    await inter.respond(type=_type)


async def start_wait(bot: Waitable, startable: Startable, event: str = 'button_click',
                     check: Optional[Callable[[Interaction], Any]] = None,
                     start_args: Any = ()):
    await startable.start(*start_args)
    await bot.wait_for(event=event, check=check or (lambda inter: inter.custom_id == 'continue'))
