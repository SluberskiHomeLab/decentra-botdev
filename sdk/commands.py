"""Slash command registration and context for the Decentra Bot SDK."""
from __future__ import annotations
from typing import Callable, Any
from dataclasses import dataclass, field


@dataclass
class SlashCommandParam:
    """A parameter for a slash command."""
    name: str
    description: str = ''
    param_type: str = 'string'  # string, integer, boolean, user, channel
    required: bool = False
    choices: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            'name': self.name,
            'description': self.description,
            'type': self.param_type,
            'required': self.required,
        }
        if self.choices:
            d['choices'] = self.choices
        return d


@dataclass
class SlashCommandContext:
    """Context passed to a slash command handler."""
    command_name: str = ''
    arguments: dict[str, Any] = field(default_factory=dict)
    user: str = ''
    server_id: str = ''
    channel_id: str = ''
    _bot: Any = None  # Reference to DecentraBot for reply methods

    async def reply(self, content: str) -> dict[str, Any] | None:
        """Send a reply message in the same channel."""
        if self._bot and self.server_id and self.channel_id:
            return await self._bot.send_message(
                server_id=self.server_id,
                channel_id=self.channel_id,
                content=content,
            )
        return None


def slash_command(
    name: str,
    description: str = '',
    parameters: list[SlashCommandParam] | None = None,
):
    """Decorator to register a function as a slash command handler."""
    def decorator(func: Callable) -> Callable:
        func._decentra_slash_command = {
            'name': name,
            'description': description,
            'parameters': [p.to_dict() for p in (parameters or [])],
        }
        return func
    return decorator
