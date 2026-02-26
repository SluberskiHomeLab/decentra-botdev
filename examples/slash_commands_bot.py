"""Example: slash command bot demonstrating command registration and handling."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import DecentraBot
from sdk.commands import SlashCommandParam

bot = DecentraBot()


@bot.slash_command(
    name='hello',
    description='Say hello to someone!',
    parameters=[
        SlashCommandParam(name='name', description='Who to greet', param_type='string', required=False),
    ],
)
async def hello_command(ctx):
    name = ctx.arguments.get('name', ctx.user)
    await ctx.reply(f'Hello, {name}! 👋')


@bot.slash_command(
    name='roll',
    description='Roll a dice (1-6)',
)
async def roll_command(ctx):
    import random
    result = random.randint(1, 6)
    await ctx.reply(f'🎲 {ctx.user} rolled a **{result}**!')


@bot.slash_command(
    name='info',
    description='Show bot info',
)
async def info_command(ctx):
    servers = await bot.get_servers()
    await ctx.reply(
        f'🤖 **Slash Command Bot**\n'
        f'Active in {len(servers)} server(s)\n'
        f'Commands: /hello, /roll, /info'
    )


if __name__ == '__main__':
    print('Starting Slash Command Bot...')
    bot.run()
