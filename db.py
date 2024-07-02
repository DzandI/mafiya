import sqlite3
import random

def mafiya_name():
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = "SELECT username FROM players WHERE role= 'mafiya' "
    curs.execute(request)
    result = curs.fetchall()
    names=""
    for i in result: # для красивого вывода в строчку
        name=i[0]
        names +=name + "\n"
    con.close()
    return names

def len_people():
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = "SELECT * FROM players"
    curs.execute(request)
    result = curs.fetchall()
    con.close()
    return len(result)

def alive_people():
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = "SELECT username FROM players WHERE dead = 0 "
    curs.execute(request)
    result = curs.fetchall()
    result = [i[0] for i in result]
    con.close()
    return result

def ides():
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = "SELECT player_id, role FROM players "
    curs.execute(request)
    result = curs.fetchall()
    con.close()
    return result

def add_player(player_id, username):
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = f"INSERT INTO players (player_id, username) VALUES ('{player_id}','{username}')"
    curs.execute(request)
    con.commit()
    con.close()

def set_roles(count_players):
    game_role = ['mirniy'] * count_players
    mafiy = int(count_players*0.3)

    for i in range(mafiy):
        game_role[i] = "mafiy"

    random.shuffle(game_role)

    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = "SELECT player_id FROM players"
    curs.execute(request)
    result=curs.fetchall()
    for role, id in zip(game_role, result):
        request = f"UPDATE players SET role = '{role}' where player_id = '{id[0]}' "
        curs.execute(request)
    con.commit()
    con.close()

def golos(role_vote, username, player_id):
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    request = f"SELECT username FROM players WHERE player_id = {player_id} and voted=0 and dead=0 "
    curs.execute(request)
    result = curs.fetchall()

    if result:
        curs.execute(f"UPDATE players SET {role_vote} = {role_vote}+1 WHERE username = '{username}'")
        curs.execute(f"UPDATE players SET voted = 1 WHERE player_id = {player_id}")
        con.commit()
        con.close()
        return True
    
    con.close()
    return False

def kill_mafiy():
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    curs.execute(f'SELECT MAX(mafia_vote) FROM players')
    max_vote = curs.fetchone()[0]
    
    request = "SELECT COUNT(*) FROM players WHERE role = 'mafiy' and dead = 0"
    curs.execute(request)
    live_mafiy = curs.fetchone()[0]

    user_kill = 'Никого'
    if max_vote == live_mafiy:

        curs.execute(f"SELECT username FROM players WHERE mafia_vote = {max_vote}")
        user_kill = curs.fetchone()[0]

        request = f"UPDATE players SET dead = 1 WHERE username = '{user_kill}' "
        curs.execute(request)
        con.commit()
        con.close()
    con.close()
    return user_kill

def kill_mir():

    con = sqlite3.connect('db.db')
    curs = con.cursor()
    curs.execute(f'SELECT MAX(citizen_vote) FROM players')
    max_vote = curs.fetchone()[0]
    
    request = f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_vote}"
    curs.execute(request)
    live_all = curs.fetchone()[0]

    user_kill = 'Никого'
    if  live_all == 1:

        curs.execute(f"SELECT username FROM players WHERE citizen_vote = {max_vote}")
        user_kill = curs.fetchone()[0]
        
        request = f"UPDATE players SET dead = 1 WHERE username = '{user_kill}' "
        curs.execute(request)
        con.commit()
        con.close()
    con.close()
    return user_kill


def check_winner():
    con = sqlite3.connect('db.db')
    curs = con.cursor()

    request = f"SELECT COUNT(*) FROM players WHERE role = 'mafiy' and dead = 0"
    curs.execute(request)
    maf_alive = curs.fetchone()[0]
    
    request = f"SELECT COUNT(*) FROM players WHERE role != 'mafiy' and dead = 0"
    curs.execute(request)
    mir_alive = curs.fetchone()[0]
    if maf_alive >= mir_alive:
        return 'Мафия'
    if maf_alive == 0:
        return 'Мирные'
    
def clear(dead=False):
    con = sqlite3.connect('db.db')
    curs = con.cursor()
    sql=f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0 "
    if dead:
        sql += ', dead = 0'
    curs.execute(sql)
    con.commit()
    con.close()