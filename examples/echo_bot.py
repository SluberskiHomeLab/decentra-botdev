"""Example: simple echo bot that replies to !ping and echoes !echo messages."""
import sys
import os

# Allow running from the decentra-botdev directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import DecentraBot

bot = DecentraBot()


@bot.on_message()
async def handle_message(message):
    # Ignore messages from bots (including ourselves)
    if message.is_bot:
        return

    if message.content.strip() == '!ping':
        await bot.send_message(
            server_id=message.server_id,
            channel_id=message.channel_id,
            content='Pong! 🏓',
        )

    elif message.content.startswith('!echo '):
        text = message.content[6:].strip()
        if text:
            await bot.send_message(
                server_id=message.server_id,
                channel_id=message.channel_id,
                content=text,
            )


if __name__ == '__main__':
    print('Starting Echo Bot...')
    bot.run()
