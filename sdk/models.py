"""Data models for the Decentra Bot SDK."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    """Represents a chat message."""
    id: int | None = None
    username: str = ''
    content: str = ''
    timestamp: str = ''
    server_id: str = ''
    channel_id: str = ''
    context: str = ''
    context_id: str = ''
    is_bot: bool = False
    edited_at: str | None = None
    reactions: list[dict[str, Any]] = field(default_factory=list)
    attachments: list[dict[str, Any]] = field(default_factory=list)
    mentions: list[str] = field(default_factory=list)
    reply_data: dict[str, Any] | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_event(cls, data: dict[str, Any]) -> 'Message':
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            content=data.get('content', ''),
            timestamp=data.get('timestamp', ''),
            server_id=data.get('server_id', ''),
            channel_id=data.get('channel_id', ''),
            context=data.get('context', ''),
            context_id=data.get('context_id', ''),
            is_bot=data.get('is_bot', False),
            edited_at=data.get('edited_at'),
            reactions=data.get('reactions', []),
            attachments=data.get('attachments', []),
            mentions=data.get('mentions', []),
            reply_data=data.get('reply_data'),
            raw=data,
        )


@dataclass
class Server:
    """Represents a server the bot is in."""
    server_id: str = ''
    name: str = ''
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Server':
        return cls(
            server_id=data.get('server_id', ''),
            name=data.get('name', ''),
            raw=data,
        )


@dataclass
class Channel:
    """Represents a channel in a server."""
    channel_id: str = ''
    name: str = ''
    channel_type: str = 'text'
    server_id: str = ''
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Channel':
        return cls(
            channel_id=data.get('channel_id', data.get('id', '')),
            name=data.get('name', ''),
            channel_type=data.get('channel_type', data.get('type', 'text')),
            server_id=data.get('server_id', ''),
            raw=data,
        )


@dataclass
class Member:
    """Represents a server member."""
    username: str = ''
    is_owner: bool = False
    is_bot: bool = False
    user_status: str = 'offline'
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Member':
        return cls(
            username=data.get('username', ''),
            is_owner=data.get('is_owner', False),
            is_bot=data.get('is_bot', False),
            user_status=data.get('user_status', 'offline'),
            raw=data,
        )
