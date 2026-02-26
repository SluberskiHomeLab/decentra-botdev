# Decentra Bot Development SDK

Build bots for Decentra — a decentralized, end-to-end encrypted chat platform.

## Quick Start

### 1. Create a Bot

1. Open your Decentra instance
2. Go to **Admin Settings → Bots → Create Bot**
3. Configure permissions (scopes) and event subscriptions (intents)
4. Copy the bot token — **it's shown only once!**

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your instance URL and bot token
```

### 3. Run with Docker

```bash
docker build -t my-decentra-bot .
docker run --env-file .env my-decentra-bot
```

### 4. Run Locally

```bash
pip install -r requirements.txt
python examples/echo_bot.py
```

## Project Structure

```
decentra-botdev/
├── sdk/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Main bot client (WS + REST)
│   ├── events.py            # Event types and handler decorators
│   ├── commands.py          # Slash command registration
│   └── models.py            # Data models (Message, Server, etc.)
├── examples/
│   ├── echo_bot.py          # Simple echo bot example
│   ├── moderation_bot.py    # Moderation commands example
│   └── slash_commands_bot.py # Slash command example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `DECENTRA_INSTANCE_URL` | URL of your Decentra instance (e.g., `https://chat.example.com`) | Yes |
| `DECENTRA_BOT_TOKEN` | Bot token from Admin Settings | Yes |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | No (default: `INFO`) |

## SDK Usage

```python
from sdk import DecentraBot, on_message, slash_command

bot = DecentraBot()

@bot.on_message()
async def handle_message(message):
    if message.content == "!ping":
        await bot.send_message(
            channel_id=message.channel_id,
            server_id=message.server_id,
            content="Pong! 🏓"
        )

@bot.slash_command(name="hello", description="Say hello!")
async def hello_command(ctx):
    await ctx.reply(f"Hello, {ctx.user}! 👋")

bot.run()
```

## Authentication

Bots connect using two methods simultaneously:

- **WebSocket** — receives real-time events (messages, members, reactions, etc.)
- **REST API** — sends messages, manages commands, queries data

The SDK handles both connections automatically.

## Scopes & Intents

**Scopes** control what API actions the bot can perform:
- `READ_MESSAGES`, `SEND_MESSAGES`, `MANAGE_MESSAGES`
- `READ_MEMBERS`, `MANAGE_MEMBERS`
- `MANAGE_CHANNELS`, `MANAGE_ROLES`
- `ADD_REACTIONS`, `MANAGE_THREADS`
- `USE_SLASH_COMMANDS`, `SEND_DMS`
- `MANAGE_SERVER`, `READ_VOICE_STATE`
- `ADMINISTRATOR` (all permissions)

**Intents** control what events the bot receives:
- `GUILD_MESSAGES`, `GUILD_MEMBERS`, `GUILD_REACTIONS`
- `GUILD_CHANNELS`, `GUILD_ROLES`, `GUILD_VOICE_STATE`
- `GUILD_THREADS`, `GUILD_POLLS`
- `DIRECT_MESSAGES`, `SLASH_COMMANDS`

## Rate Limits

Bots have configurable rate limits (set by the instance admin):
- **Messages**: Default 30 messages per 10 seconds per channel
- **API Calls**: Default 120 requests per minute

The SDK automatically handles rate limiting with backoff.

## License

MIT — See the main Decentra repository for full license details.
