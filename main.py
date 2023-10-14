from os import listdir
import disnake
from disnake.ext import commands

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
TOKEN = "MTEzNTk2MjIyNTE3NDExODUyMQ.GnzWA0.FFfv5TXIysxeozE1IOjvuh0aeGSxAKievN0Ldc"
bot = commands.Bot(command_prefix="#", help_command=None, intents=intents)

# Создаём команду
@bot.command()
# Определяет создателя бота
@commands.is_owner()
# Загрузка Cog
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


@bot.command()
@commands.is_owner()
# Отгрузка Cog
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


@bot.command()
@commands.is_owner()
# Перезагрузка Cog
async def reload(ctx, extension):
    bot.reload_extension(f"cogs.{extension}")



for filename in listdir("Cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cogs.{filename[:-3]}")
bot.run(TOKEN)
