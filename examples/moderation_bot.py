"""Example: moderation bot with slash commands for server management."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import DecentraBot

bot = DecentraBot()

# Track warnings per user per server
warnings: dict[str, dict[str, int]] = {}  # {server_id: {username: count}}

# Bad word filter (simple example)
BAD_WORDS = {'spam', 'badword'}


@bot.on_message()
async def auto_moderate(message):
    """Automatically delete messages containing bad words."""
    if message.is_bot:
        return

    content_lower = message.content.lower()
    if any(word in content_lower for word in BAD_WORDS):
        if message.id:
            await bot.delete_message(message.id)
            await bot.send_message(
                server_id=message.server_id,
                channel_id=message.channel_id,
                content=f'⚠️ Message from **{message.username}** was removed (content policy).',
            )


@bot.slash_command(name='warn', description='Issue a warning to a user')
async def warn_command(ctx):
    target = ctx.arguments.get('user', '')
    if not target:
        await ctx.reply('Usage: /warn <username>')
        return

    server_warns = warnings.setdefault(ctx.server_id, {})
    server_warns[target] = server_warns.get(target, 0) + 1
    count = server_warns[target]

    await ctx.reply(f'⚠️ **{target}** has been warned. (Total warnings: {count})')


@bot.slash_command(name='warnings', description='Check warning count for a user')
async def warnings_command(ctx):
    target = ctx.arguments.get('user', ctx.user)
    server_warns = warnings.get(ctx.server_id, {})
    count = server_warns.get(target, 0)
    await ctx.reply(f'📋 **{target}** has {count} warning(s).')


@bot.slash_command(name='serverinfo', description='Show server information')
async def serverinfo_command(ctx):
    try:
        members = await bot.get_members(ctx.server_id)
        channels = await bot.get_channels(ctx.server_id)
        bot_count = sum(1 for m in members if m.is_bot)
        human_count = len(members) - bot_count

        await ctx.reply(
            f'📊 **Server Info**\n'
            f'Members: {human_count} humans, {bot_count} bots\n'
            f'Channels: {len(channels)}\n'
        )
    except Exception as e:
        await ctx.reply(f'Failed to get server info: {e}')


if __name__ == '__main__':
    print('Starting Moderation Bot...')
    bot.run()
