"""Main Decentra Bot client — handles WebSocket events and REST API calls."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import ssl
import time
from typing import Any, Callable, Coroutine
from urllib.parse import urljoin

import aiohttp
import websockets
from dotenv import load_dotenv

from .models import Message, Server, Channel, Member
from .commands import SlashCommandContext
from .events import SLASH_COMMAND

load_dotenv()

logger = logging.getLogger('decentra-bot')


class DecentraBot:
    """High-level bot client for Decentra.

    Connects via WebSocket for real-time events and uses REST API for actions.

    Usage::

        bot = DecentraBot()

        @bot.on_message()
        async def handle(msg):
            if msg.content == '!ping':
                await bot.send_message(msg.server_id, msg.channel_id, 'Pong!')

        bot.run()
    """

    def __init__(
        self,
        instance_url: str | None = None,
        token: str | None = None,
        log_level: str | None = None,
    ):
        self.instance_url = (instance_url or os.getenv('DECENTRA_INSTANCE_URL', '')).rstrip('/')
        self.token = token or os.getenv('DECENTRA_BOT_TOKEN', '')
        self._log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')

        logging.basicConfig(
            level=getattr(logging, self._log_level.upper(), logging.INFO),
            format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        )

        if not self.instance_url:
            raise ValueError('DECENTRA_INSTANCE_URL is required')
        if not self.token:
            raise ValueError('DECENTRA_BOT_TOKEN is required')

        # Event handlers: event_name → list of async callables
        self._event_handlers: dict[str, list[Callable[..., Coroutine]]] = {}
        # Slash command handlers: command_name → async callable
        self._slash_handlers: dict[str, Callable[..., Coroutine]] = {}
        # Slash command definitions for registration
        self._slash_definitions: list[dict[str, Any]] = []

        self._ws: Any = None
        self._session: aiohttp.ClientSession | None = None
        self._running = False

        # Auto-discover decorated methods (for subclass pattern)
        self._discover_handlers()

    # ── Handler registration ────────────────────────────────────────

    def _discover_handlers(self) -> None:
        """Find methods decorated with @on_message, @slash_command, etc."""
        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)
            except Exception:
                continue
            if callable(attr):
                event = getattr(attr, '_decentra_event', None)
                if event:
                    self.add_event_handler(event, attr)
                cmd_def = getattr(attr, '_decentra_slash_command', None)
                if cmd_def:
                    self._slash_handlers[cmd_def['name']] = attr
                    self._slash_definitions.append(cmd_def)

    def add_event_handler(self, event: str, handler: Callable[..., Coroutine]) -> None:
        self._event_handlers.setdefault(event, []).append(handler)

    def on_message(self):
        """Decorator to register a message handler on an instance."""
        def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            self.add_event_handler('message_create', func)
            return func
        return decorator

    def on_event(self, event_name: str):
        """Decorator to register a generic event handler on an instance."""
        def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            self.add_event_handler(event_name, func)
            return func
        return decorator

    def slash_command(self, name: str, description: str = '', parameters: list | None = None):
        """Decorator to register a slash command handler on an instance."""
        def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
            self._slash_handlers[name] = func
            self._slash_definitions.append({
                'name': name,
                'description': description,
                'parameters': [p.to_dict() if hasattr(p, 'to_dict') else p for p in (parameters or [])],
            })
            return func
        return decorator

    # ── REST API helpers ────────────────────────────────────────────

    def _api_url(self, path: str) -> str:
        return urljoin(self.instance_url + '/', path.lstrip('/'))

    def _headers(self) -> dict[str, str]:
        return {
            'Authorization': f'Bot {self.token}',
            'Content-Type': 'application/json',
        }

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            # Allow self-signed certs (common in dev)
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_ctx)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def _api_request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        session = await self._ensure_session()
        url = self._api_url(path)
        async with session.request(method, url, headers=self._headers(), **kwargs) as resp:
            data = await resp.json()
            if resp.status >= 400:
                logger.error('API %s %s → %s: %s', method, path, resp.status, data)
            return data

    # ── Public REST API methods ─────────────────────────────────────

    async def send_message(self, server_id: str, channel_id: str, content: str) -> dict[str, Any]:
        """Send a message to a server channel."""
        return await self._api_request('POST', '/api/bot/messages', json={
            'server_id': server_id,
            'channel_id': channel_id,
            'content': content,
        })

    async def edit_message(self, message_id: int, content: str) -> dict[str, Any]:
        """Edit a message the bot sent."""
        return await self._api_request('PUT', f'/api/bot/messages/{message_id}', json={
            'content': content,
        })

    async def delete_message(self, message_id: int) -> dict[str, Any]:
        """Delete a message."""
        return await self._api_request('DELETE', f'/api/bot/messages/{message_id}')

    async def get_servers(self) -> list[Server]:
        """Get servers the bot is a member of."""
        data = await self._api_request('GET', '/api/bot/servers')
        return [Server.from_dict(s) for s in data.get('servers', [])]

    async def get_channels(self, server_id: str) -> list[Channel]:
        """Get channels in a server."""
        data = await self._api_request('GET', f'/api/bot/servers/{server_id}/channels')
        return [Channel.from_dict(c) for c in data.get('channels', [])]

    async def get_members(self, server_id: str) -> list[Member]:
        """Get members in a server."""
        data = await self._api_request('GET', f'/api/bot/servers/{server_id}/members')
        return [Member.from_dict(m) for m in data.get('members', [])]

    async def get_messages(self, server_id: str, channel_id: str, limit: int = 50) -> list[Message]:
        """Get recent messages from a channel."""
        data = await self._api_request('GET', f'/api/bot/servers/{server_id}/channels/{channel_id}/messages?limit={limit}')
        return [Message.from_event(m) for m in data.get('messages', [])]

    async def add_reaction(self, message_id: int, emoji: str) -> dict[str, Any]:
        """Add a reaction to a message."""
        return await self._api_request('POST', f'/api/bot/messages/{message_id}/reactions', json={
            'emoji': emoji,
        })

    async def register_commands(self) -> dict[str, Any]:
        """Register all slash commands with the server."""
        if not self._slash_definitions:
            return {'success': True, 'message': 'No commands to register'}
        return await self._api_request('POST', '/api/bot/commands', json={
            'commands': self._slash_definitions,
        })

    # ── WebSocket connection ────────────────────────────────────────

    def _ws_url(self) -> str:
        url = self.instance_url.replace('http://', 'ws://').replace('https://', 'wss://')
        return f'{url}/ws'

    async def _connect_ws(self) -> None:
        ws_url = self._ws_url()
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        logger.info('Connecting to %s ...', ws_url)
        self._ws = await websockets.connect(ws_url, ssl=ssl_ctx, ping_interval=30)

        # Authenticate
        await self._ws.send(json.dumps({
            'type': 'bot_auth',
            'token': self.token,
        }))

        auth_response = await self._ws.recv()
        auth_data = json.loads(auth_response)
        if auth_data.get('type') == 'bot_auth_success':
            logger.info('✓ Authenticated as %s (bot_id=%s)', auth_data.get('username'), auth_data.get('bot_id'))
        elif auth_data.get('type') == 'error':
            raise ConnectionError(f'Authentication failed: {auth_data.get("message")}')
        else:
            logger.warning('Unexpected auth response: %s', auth_data)

    async def _ws_loop(self) -> None:
        """Main WebSocket event loop."""
        while self._running:
            try:
                await self._connect_ws()

                # Register slash commands after connecting
                if self._slash_definitions:
                    result = await self.register_commands()
                    logger.info('Registered %d slash commands: %s', len(self._slash_definitions), result)

                async for raw_message in self._ws:
                    try:
                        data = json.loads(raw_message)
                        await self._dispatch_event(data)
                    except json.JSONDecodeError:
                        logger.warning('Received non-JSON message')
                    except Exception as e:
                        logger.error('Error handling event: %s', e, exc_info=True)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning('WebSocket closed: %s — reconnecting in 5s', e)
            except ConnectionError as e:
                logger.error('Connection error: %s — retrying in 10s', e)
                await asyncio.sleep(10)
                continue
            except Exception as e:
                logger.error('Unexpected error: %s — reconnecting in 5s', e, exc_info=True)

            if self._running:
                await asyncio.sleep(5)

    async def _dispatch_event(self, data: dict[str, Any]) -> None:
        """Dispatch an event to registered handlers."""
        event_type = data.get('type', '')

        if event_type == 'bot_event':
            event_name = data.get('event', '')
            event_data = data.get('data', {})
            event_data['server_id'] = data.get('server_id', '')
            event_data['channel_id'] = data.get('channel_id', '')

            # Handle slash commands specially
            if event_name == 'slash_command':
                cmd_name = event_data.get('command', '')
                handler = self._slash_handlers.get(cmd_name)
                if handler:
                    ctx = SlashCommandContext(
                        command_name=cmd_name,
                        arguments=event_data.get('arguments', {}),
                        user=event_data.get('user', ''),
                        server_id=event_data.get('server_id', ''),
                        channel_id=event_data.get('channel_id', ''),
                        _bot=self,
                    )
                    await handler(ctx)
                return

            # Dispatch to event handlers
            handlers = self._event_handlers.get(event_name, [])
            for handler in handlers:
                try:
                    if event_name == 'message_create':
                        await handler(Message.from_event(event_data))
                    else:
                        await handler(event_data)
                except Exception as e:
                    logger.error('Handler error for %s: %s', event_name, e, exc_info=True)

        elif event_type == 'pong':
            pass  # heartbeat response
        else:
            logger.debug('Unhandled WS message type: %s', event_type)

    # ── Lifecycle ───────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the bot (async)."""
        self._running = True
        logger.info('Starting Decentra bot...')
        await self._ws_loop()

    async def stop(self) -> None:
        """Stop the bot gracefully."""
        self._running = False
        if self._ws:
            await self._ws.close()
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info('Bot stopped.')

    def run(self) -> None:
        """Run the bot (blocking). Handles Ctrl+C gracefully."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            logger.info('Received shutdown signal')
            loop.run_until_complete(self.stop())
        finally:
            loop.close()
