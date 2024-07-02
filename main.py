from telebot import TeleBot
from settings import *
from random import choice
from time import *
from db import *

#создание бота
bot = TeleBot(token)

players = []
game=False
night=False

def get_killed(night):
    if not night:
        username_killed = kill_mir()
        return f"Горожане выгнали: {username_killed}"
    username_killed = kill_mafiy()
    return f"Мафия убила: {username_killed}"

def autoplay_citizen(message):
    players_roles = ides()
    for player_id, _ in players_roles:
        usernames = alive_people()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            golos('citizen_vote', vote_username, player_id)
            bot.send_message(message.chat.id, f'{name} проголосовал против {vote_username}')
            sleep(0.5)


def autoplay_mafia():
    players_roles = ides()
    for player_id, role in players_roles:
        usernames = alive_people()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames and role == 'mafiy':
            usernames.remove(name)
            vote_username = choice(usernames)

@bot.message_handler(func = lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def print_start_info(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} - добавлен в игру')

    add_player(message.from_user.id, message.from_user.first_name)

    bot.send_message(message.chat.id, f'В игре {str(len_people())} человек ')

@bot.message_handler(commands =['начало'])
def game_start(message):
    global game,night
    night = False

    len_people_game = len_people()

    if len_people_game >= 5 and not game:
        set_roles(len_people_game) # role and user_id

        role_people = ides()
        mafiya_people = mafiya_name()

        for player_id, role in role_people:
            if player_id >= 5 and not game:
                bot.send_message(player_id,text=role) # role by id
                if role=='mafiy':
                    bot.send_message(id, text=f'Другие мафиозе: \n{mafiya_people}')

        game=True
        bot.send_message(message.chat.id, text='Игра началась!')
        clear(dead=True)
        game_loop(message)
        return
    bot.send_message(message.chat.id, text='Нужно больше игроков')
    for i in range(5-len_people_game):
        bot_name = f'robot{i}'
        add_player(i, bot_name)
        bot.send_message(message.chat.id, text=f"{bot_name} добавлен!")
        sleep(0.2)
    game_start(message)


@bot.message_handler(commands =['kill'])
def kill(message):
    username = message.text[6:]
    users_alive = alive_people()
    spisok_mafiya = mafiya_name()
    if night == True and message.from_user.first_name in spisok_mafiya:
        if not username in users_alive:
            bot.send_message(message.chat.id, 'Такого игрока нет в списке выживших')
            return
        golosovanie = golos('mafia_vote', username, message.from_user.id)

        if golosovanie:
            bot.send_message(message.chat.id, "Ващ голос учтён")
            return
        
        bot.send_message(message.chat.id, "Вы больше не можете голосовать")
        return
    bot.send_message(message.chat.id, "Сейчас день. Днём мафия не может голосовать")

@bot.message_handler(commands =['kick'])
def kick(message):
    username = message.text[6:]
    users_alive = alive_people()
    if night == False:
        if not username in users_alive:
            bot.send_message(message.chat.id, 'Такого игрока нет в списке выживших')
            return
        golosovanie = golos('citizen_vote', username, message.from_user.id)

        if golosovanie:
            bot.send_message(message.chat.id, "Ваш голос учтён")
            return
        
        bot.send_message(message.chat.id, "Вы больше не можете голосовать")
        return
    bot.send_message(message.chat.id, "Сейчас ночь. Мирные спят")

@bot.message_handler(commands =['night'])
def check_night(message):
    global night
    if night == False:
        kill_user = kill_mir()
        night = True
        all_alive= alive_people()
        bot.send_message(message.chat.id, f"{all_alive}")
        bot.send_message(message.chat.id, f"Выгнали {kill_user}\nНаступила ночь")
        return
    kill_user=kill_mafiy()
    night = False
    bot.send_message(message.chat.id, f"Наступил день\nМафия убила {kill_user}")
    return

def game_loop(message):
    global night, game
    bot.send_message(message.chat.id, "Добро пожаловать в игру ! Вам даётся 1 минута, чтобы познакомиться")
    sleep(60)
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if not night:
            bot.send_message(message.chat.id, "Город засыпает, просыпается мафия.")
        else:
            bot.send_message(message.chat.id, "Город просыпается.")
        winner = check_winner()
        if winner == "Мафия" or winner == "Мирные":
            game = False
            bot.send_message(message.chat.id, text=f"Игра окончена, победили: {winner}")
            return
        clear(dead=False)
        night = not night
        alive = alive_people()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, text=f"В игре: \n{alive}")
        sleep(10)
        autoplay_mafia if night else autoplay_citizen(message)

bot.polling()