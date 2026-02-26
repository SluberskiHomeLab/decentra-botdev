"""Event handler decorators and event types for the Decentra Bot SDK."""
from __future__ import annotations
from typing import Callable, Any

# Event name constants
MESSAGE_CREATE = 'message_create'
MESSAGE_UPDATE = 'message_update'
MESSAGE_DELETE = 'message_delete'
MEMBER_JOIN = 'member_join'
MEMBER_LEAVE = 'member_leave'
MEMBER_BAN = 'member_ban'
REACTION_ADD = 'reaction_add'
REACTION_REMOVE = 'reaction_remove'
CHANNEL_CREATE = 'channel_create'
CHANNEL_UPDATE = 'channel_update'
CHANNEL_DELETE = 'channel_delete'
ROLE_CREATE = 'role_create'
ROLE_UPDATE = 'role_update'
SLASH_COMMAND = 'slash_command'
BOT_JOINED_SERVER = 'bot_joined_server'
BOT_LEFT_SERVER = 'bot_left_server'


def on_message(func: Callable | None = None):
    """Decorator to register a message_create event handler."""
    def decorator(f: Callable) -> Callable:
        f._decentra_event = MESSAGE_CREATE
        return f
    if func is not None:
        return decorator(func)
    return decorator


def on_member_join(func: Callable | None = None):
    """Decorator to register a member_join event handler."""
    def decorator(f: Callable) -> Callable:
        f._decentra_event = MEMBER_JOIN
        return f
    if func is not None:
        return decorator(func)
    return decorator


def on_member_leave(func: Callable | None = None):
    """Decorator to register a member_leave event handler."""
    def decorator(f: Callable) -> Callable:
        f._decentra_event = MEMBER_LEAVE
        return f
    if func is not None:
        return decorator(func)
    return decorator


def on_reaction(func: Callable | None = None):
    """Decorator to register a reaction_add event handler."""
    def decorator(f: Callable) -> Callable:
        f._decentra_event = REACTION_ADD
        return f
    if func is not None:
        return decorator(func)
    return decorator


def on_event(event_name: str):
    """Generic decorator to register any event handler."""
    def decorator(f: Callable) -> Callable:
        f._decentra_event = event_name
        return f
    return decorator
