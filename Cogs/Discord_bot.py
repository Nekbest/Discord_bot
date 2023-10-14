import disnake
from disnake.ext import commands
from pymorphy3 import MorphAnalyzer
from random import shuffle, randint
from requests import get

emoji = ['🛁', '🚴', '🚀', '🚁', '🚂', '🚃', '🚌', '🚎', '🚑', '🚒', '🚓', '🦆', '🚕', '🦚', '🦞', '🚗',
         '🦑', '🚚', '🦢', '🦟', '🦠', '🦅', '🦀', '🦗', '🦋', '🚜', '🦇', '🦔', '🦓', '🚣', '🦒', '🦎',
         '🚶', '🛌', '🛒', '🛩', '🛰', '🛸', '🤔', '🤐', '🤓', '🤡', '🤫', '🥐', '🥕', '🥝', '🥦', '🥾']
score = {'user': 0, 'bot': 0}
options = {"start": False, "name": "first__bot#9206"}


class MyBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.morph = MorphAnalyzer()

    # Декоратор событий в Cog(@bot.event)
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Бот {self.bot.user} подключился!")

    # Декоратор команд(@bot.command)
    @commands.command()
    async def help(self, ctx):
        await ctx.send("Я могу:\n" +
                       "1. Согласовывать слова с числительными.(/approve)\n" +
                       "2. Определять, живое ли существительное или нет.(/alive_or_not)\n" +
                       "3. Менять существительное в соответствии с введенным падежом и числом.(/case_and_number)\n" +
                       "4. Выводить слова в начальной форме.(команда /initial_form)\n" +
                       "5. Производить морфологический анализ слова.(/morph_analys)\n" +
                       "6. Игра в эмоции.(/start_game_emoji)\n" +
                       "7. Правила игры в эмоции.(/rule_emoji)")

    @commands.slash_command()
    async def approve(self, inter: disnake.ApplicationCommandInteraction, number: int, word: str):
        comment = self.morph.parse(word)[0]
        await inter.send(f"{number} {comment.make_agree_with_number(number).word}")

    @commands.slash_command()
    async def alive_or_not(self, inter: disnake.ApplicationCommandInteraction, word: str):
        comment = self.morph.parse(word)[0]
        if comment.tag.POS == "NOUN" and comment.tag.animacy == "anim":
            await inter.send(f"Существительное {word} живое!")
        elif comment.tag.POS == "NOUN" and comment.tag.animacy == "inan":
            await inter.send(f"Существительное {word} неживое!")
        else:
            await inter.send(f"Слово {word} не является существительным!")

    @commands.slash_command()
    async def case_and_number(self, inter: disnake.ApplicationCommandInteraction, word: str, case: str, number: str):
        case = case.lower()
        number = number.lower()
        comment = self.morph.parse(word)[0]
        inclined = ["NOUN", "ADJF", "NPRO", "NUMR"]
        numbers = {"множественное": "plur", "единственное": "sing"}
        cases = {"именительный": "nomn", "родительный": "gent", "дательный": "datv",
                 "винительный": "accs", "творительный": "ablt", "предложный": "loct"}
        if comment.tag.POS in inclined:
            await inter.send(f"Слово {word.upper()} в {case[:-2]}ом падеже и {number[:-2]}ом числе:" +
                             f"{comment.inflect({numbers[number], cases[case]}).word}")
        else:
            await inter.send("Не склоняемая часть речи!")

    @commands.slash_command()
    async def initial_form(self, inter: disnake.ApplicationCommandInteraction, word: str):
        await inter.send(f"Начальная форма слова {word} - {self.morph.parse(word)[0].normal_form}")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.content == "/start_game_emoji" and options["start"] != 1:
            options["name"] = msg.author
            options["start"] = True
            shuffle(emoji)
            await msg.channel.send('Игра началась!\nЕсли вам интересны правила пропишите команду /rule_emoji')
        elif msg.content == '/stop' and options["name"] == msg.author:
            options["name"] = "first__bot#9206"
            options["start"] = False
            score['user'] = 0
            score['bot'] = 0
            await msg.channel.send('Пока!')
        elif msg.content == '/rule_emoji' and options["name"] == msg.author:
            await msg.channel.send('У нашего бота есть в запасе много смайликов.\n' +
                                   'По очереди с ботом будем называть любое число' +
                                   '— номер смайла, которого нужно вытащить из запаса.\n' +
                                   'Если номер больше, чем количество оставшихся в запасе смайликов' +
                                   ', то берется номер,' +
                                   'равный остатку от деления названного числа на количество оставшихся.\n' +
                                   'В каждой паре сравниваются числовые значения unicode-символов' +
                                   'и определяется победитель данного раунда.\n' +
                                   'После раунда смайлы перемешиваются, выводятся смайлы,' +
                                   'вытащенные пользователем и ботом, а также текущий счёт.\n' +
                                   'Игра продолжается до последнего смайлика или до сообщения пользователя /stop.\n' +
                                   'По окончании выводится чемпион. При прерывании командой /stop счёт обнуляется.\n')
        elif options["start"] == 1 and options["name"] == msg.author:
            try:
                if emoji:
                    bot_choice = randint(0, 100) % len(emoji)
                    msg.content = int(msg.content) % len(emoji)
                    await msg.channel.send(f"Итоговый номер вашей эмоции: {msg.content}")
                    await msg.channel.send(f"Номер эмоции бота: {bot_choice}")
                    await msg.channel.send(f"Ваша эмоция {emoji[msg.content]}")
                    emoji.pop(msg.content)
                    await msg.channel.send(f"Эмоция бота: {emoji[bot_choice]}")
                    emoji.pop(bot_choice)
                    if msg.content > bot_choice:
                        score["user"] += 1
                    elif bot_choice > msg.content:
                        score["bot"] += 1
                    await msg.channel.send(f'Ты: {score["user"]} - Бот: {score["bot"]}')
                else:
                    raise IndexError
            except IndexError:
                if score["user"] > score["bot"]:
                    await msg.channel.send(f'Эмоции кончились!\nРезультат: Вы {score["user"]} - Бот {score["bot"]}\n' +
                                           'Вы выиграли!')
                elif score["user"] < score["bot"]:
                    await msg.channel.send(f'Эмоции кончились!\nРезультат: Вы {score["user"]} - Бот {score["bot"]}\n' +
                                           'Бот победил!')
                else:
                    await msg.channel.send(f'Эмоции кончились!\nРезультат: Вы {score["user"]} - Бот {score["bot"]}\n' +
                                           'Ничья!')
                options["name"] = "first__bot#9206"
                options["start"] = False
                score['user'] = 0
                score['bot'] = 0
            except Exception as e:
                await msg.channel.send('Неправильный ввод!')



def setup(bot):
    bot.add_cog(MyBot(bot))
