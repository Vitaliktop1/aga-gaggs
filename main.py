import aminofix
import random
import websocket
import time
import json

from requests import Session
from threading import Thread
from aminofix.lib.util import signature
from threading import Thread

email = ("senavlad604@gmail.com")
password = ("123454321")
client = aminofix.Client()
client.login(email, password)

day = open("day.gif", "br")
night = open("night.gif", "br")
session = Session()
result = {}
activity_games = {}
buffer_game = {}

roles = ["Самоубийца.", "Алкоголик."]
roles_2 = ["Сержант.", "Адвокат."]

def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

def role_text(role):
    message = f"Приветствую, игрок.\nТвоя роль - {role}\n"
    if role == "Мирный житель.":
        message += "ваша задача - вычислить игроков команды Мафии и устранить их всех на дневном голосовании."

    elif role == "Мафиози.":
        message += "Вы - член мафиозной семьи. ночью вместе с семьёй выбираете жертву. можете стать новым Доном, если прежнего убьют."

    elif role == "Сержант.":
        message += " вы помощник Комиссара. вы видите все ночные ходы и проверки комиссара. но самих ночных ходов у вас нет, вы можете только голосовать днем со всеми мирными жителями. однако, если комиссар погибает, вы повышаетесь до его звания и сами становитесь комом."

    elif role == "Комиссар.":
        message += "вы мирный, обладающий уникальными возможностями. каждую игровую ночь вы имеете право проверить чьи либо документы. либо сделать выстрел – то есть убить подозреваемого или проверенного игрока."

    elif role == "Самоубийца.":
        message += "нейтральная роль, побеждающая только умерев на дневном голосовании."

    elif role == "Алкоголик.":
        message += "ночью вы ходите по ночным улицам, и можете стать свидетелем случайного события."

    elif role == "Адвокат.":
        message += "ваша цель - выбрать случайного игрока и защищать его на дневном голосовании."

    elif role == "Врач.":
        message += "лечите людей. Можете угадать кого убьет мафия. используйте команду !лечить [ссылка]"

    elif role == "Дон.":
        message += "Ваша роль - Дон. Глава мафии, учавствующий во всех событиях, и имеющий большее влияние."

    return message

def distribution(users):
    users = len(users)
    if users >= 4:
        kit = ["Мирный житель.", "Мирный житель.", "Дон.", "Врач."]

    if users >= 5:
        kit.append("Комиссар.")

    if users >= 6:
        random_role = random.choice(roles)
        kit.append(random_role)
        roles.remove(random_role)
    
    if users >= 7:
        kit.append("Мафиози.")

    if users >= 8:
        kit.append("Мирный житель.")

    if users >= 9:
        random_role = random.choice(roles_2)
        kit.append(random_role)
        roles.remove(random_role)

    if users >= 10:
        kit.append("Мафиози.")

    if users >= 11:
        random_role = random.choice(roles)
        kit.append(random_role)
        roles.remove(random_role)

    if users == 12:
        kit.append("Мафиози.")

    return kit


def on_message(data):
    try:
        ndc = data['ndcId']
        if ndc == 0:
            return
    except:
        return
    try:
        user = data['chatMessage']['author']['uid']
    except:
        user = None
    try:
        nickname = data['chatMessage']['author']['nickname']
    except:
        nickname = None
    try:
        content = data['chatMessage']['content']
    except:
        return
    try:
        chat = data['chatMessage']['threadId']
    except:
        chat = None
    try:
        id = data['chatMessage']['messageId']
    except:
        id = None
    try:
        content_str = data['chatMessage']['content']
    except:
        content_str = None
    communityid = str(ndc)

    print(f"{nickname}: {content} / {ndc} / {user} ")
    
    print(len(result))
    if communityid in result.keys():
        sub_client = result[communityid]
    else:
        print("no")
        try:
            sbc = aminofix.SubClient(comId=communityid, profile=client.profile)
            result[communityid] = sbc
            sub_client = sbc
        except Exception as e:
            print(e)
            return

    def check_game():
        if communityid not in activity_games:
            sub_client.send_web_message(chatId=chat, message="Набор в игру закрыт.")
            return False

        elif activity_games[communityid]["started"]:
            sub_client.send_web_message(chatId=chat, message="Игра уже начата.")
            return False

        return True

    content = content.split()

    if content[0][0] == "!":
        comand = content[0][1:]
        if comand == "правила":
            sub_client.send_web_message(chatId=chat, message="""[C]В мирном горое появляется мафия, и честные жители больше не могут спать спокойно: им нужно вычислить, кто есть кто и линчевать всю мафию, чтобы спастись. Если им не удасться это сделать, мафия захватит город, и мирные жители будут обречены.

[CUI]!набор
[CUI]Позволяет открыть набор.

[CUI]!старт
[CUI]Позволяет начать игру.

[CUI]!присоединиться
[CUI]Присоединяет к игре.

[CUI]!голосовать [ссылка]
[CUI]отдает голос за казнение тегнутого игрока.

[CUI]!войти [ссылка на чат]
[CUI]бот входит в чат, даже если тот в другом соо.""")


        elif comand == "набор":
            if communityid in activity_games:
                sub_client.send_web_message(chatId=chat, message="Невозможно набрать игроков в игру, пока она не завершена.")
                return

            activity_games[communityid] = {"day": 0, "started": False, "users":[user], "initial_chat": chat, "times": "night"}

            sub_client.send_web_message(chatId=chat, message="[CUI]Открыт набор в игру!\n[CI]Пропиши !присоединиться\n[CI]Чтобы присоединяет к игре.")

        elif comand == "войти":
            link_data = client.get_from_code(content_str.split()[1])
            client.join_community(comId=link_data.comId)
            sec_sub_client = aminofix.SubClient(comId=link_data.comId, profile=client.profile)
            sub_client.join_chat(chatId=link_data.objectId)


        elif comand == "присоединиться":
            if not check_game():
                return

            elif user in activity_games[communityid]["users"]:
                sub_client.send_web_message(chatId=chat, message="Ты и так в игре.")
                return

            elif len(activity_games[communityid]["users"]) == 12:
                sub_client.send_web_message(chatId=chat, message="Все места заполнены.")
                return

            activity_games[communityid]["users"].append(user)
            sub_client.send_web_message(chatId=chat, message="Успешно присоединили к набору.")


        elif comand == "старт":
            if not check_game():
                return

            elif user not in activity_games[communityid]["users"]:
                sub_client.send_web_message(chatId=chat, message="Вы не можете начать игру, так как не являетесь участником.")
                return

            elif len(activity_games[communityid]["users"]) < 4:
                sub_client.send_web_message(chatId=chat, message="Недостаточно игроков для начала игры.\nМиннимальное количество - 4.")
                return

            sub_client.send_web_message(chatId=chat, message="Перемешиваем игроков и распределяем роли...")
            sub_client.edit_chat(viewOnly=True, chatId=chat)
            activity_games[communityid]["started"] = True
            roles_list = distribution(activity_games[communityid]["users"])
            random.shuffle(activity_games[communityid]["users"])
            users = {}
            roles = {}
            mafia = []
            peaceful = []
            mafia_chat = ""
            ser_chat = None
            ser = None
            for user, role in zip(activity_games[communityid]["users"], roles_list):
                users[user] = role
                roles[role] = user
                if role not in ["Дон.", "Мафиози."]:
                    peaceful.append(user)
                if role in ["Дон.", "Мафиози."]:
                    mafia.append(user)
                elif role == "Сержант.":
                    data = json.dumps({
                    "title": "Mafia_chat",
                    "inviteeUids": user,
                    "initialMessageContent": "Это - чат сержанта.",
                    "content": "Mafia_Chat",
                    "type":0,
                    "publishToGlobal": 0,
                    "timestamp": int(time.time() * 1000)
                    })
                    response = session.post(f"{client.api}/x{communityid}/s/chat/thread", data=data, headers=client.parse_headers(data=data, sig=signature(data)))
                    if response.status_code == 200:
                        ser = json.loads(response.text)["thread"]["threadId"]
                else:
                    print(user)
                    sub_client.start_chat(userId=user, message=role_text(role))
                    time.sleep(6)
            t = Thread(target=sub_client.send_message, kwargs={"chatId":chat, "file":night, "fileType":"gif"})
            t.start()
            data = json.dumps({
                    "title": "Mafia_chat",
                    "inviteeUids": mafia,
                    "initialMessageContent": "Это - чат мафии.\nЧтобы проголосовать - пишите !голосовать [ссылка].",
                    "content": "Mafia_Chat",
                    "type":0,
                    "publishToGlobal": 0,
                    "timestamp": int(time.time() * 1000)
                })
            response = session.post(f"{client.api}/x{communityid}/s/chat/thread", data=data, headers=client.parse_headers(data=data, sig=signature(data)))
            print(response.text)
            mafia_chat = json.loads(response.text)["thread"]["threadId"]
            for usr in mafia:
                sub_client.send_web_message(chatId=mafia_chat, message=role_text(users[usr]))
            activity_games[communityid]["users"] = users
            buffer_game[communityid] = {"player_role":roles, "all_role_in_game":roles_list, "mafia_chat": mafia_chat, "sershant": ser_chat, "mafia": mafia, "accept":activity_games[communityid]["users"], "golosa":{}, "accept_mafia": mafia, "peaceful": peaceful, "heal": ""}
            t.join()
            sub_client.send_web_message(chatId=chat, message=f"Ночь {activity_games[communityid]['day']}\nНа улицы города выходят лишь самые отважные и бесстрашные. Утром попробуем сосчитать их головы...")

        elif comand == "голосовать":
            if user not in activity_games[communityid]["users"]:
                sub_client.send_web_message(chatId=chat, message="Вы не в игре.")
                return

            if activity_games[communityid]["times"] == "night":
                if user in buffer_game[communityid]["mafia"]:
                    userId = client.get_from_code(content_str.split()[1]).objectId
                    if userId != buffer_game[communityid]["player_role"]["Дон."] and userId != user and userId in activity_games[communityid]['users']:
                        if user in buffer_game[communityid]["accept_mafia"]:
                            buffer_game[communityid]["accept_mafia"].remove(user)
                            if userId not in buffer_game[communityid]["golosa"]:
                                buffer_game[communityid]["golosa"].update({1:userId})
                            else:
                                res = get_key(buffer_game[communityid]["golosa"], userId)
                                res+=1
                                buffer_game[communityid]["golosa"].update({res:userId})
                            
                else:
                    sub_client.send_web_message(chatId=chat, message="Вы не можете делать это ночью.")
            else:
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"{nickname} отдал свой голос.")
                userId = client.get_from_code(content_str.split()[1]).objectId
                if userId != user and userId in activity_games[communityid]['users']:
                    buffer_game[communityid]["accept"].remove(user)
                    if userId not in buffer_game[communityid]["golosa"]:
                        buffer_game[communityid]["golosa"].update({1:userId})
                    else:
                        res = get_key(buffer_game[communityid]["golosa"], userId)
                        res+=1
                        buffer_game[communityid]["golosa"].update({res:userId})


        elif comand == "лечить":
            if communityid in buffer_game and user not in activity_games[communityid]["users"]:
                sub_client.send_web_message(chatId=chat, message="Вы не в игре.")
                return
            elif get_key(activity_games[communityid]["users"], userId) == "Врач.":
                if activity_games[communityid]["times"] == "night":
                    if activity_games[communityid]["times"] == "day":
                        buffer_game[communityid]["heal"] = client.get_from_code(content_str.split()[1]).objectId

        elif communityid in buffer_game:
            if buffer_game[communityid]["accept_mafia"] == []:
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"Мафия выбрала цель.")
                top = sorted(list(buffer_game[communityid]["golosa"].keys()))[::-1][:1][0]
                top=buffer_game[communityid]["golosa"][top]
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"убили игрока, что оказался {activity_games[communityid]['users'][top]}")
                if top == buffer_game[communityid]["heal"]:
                    sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"Но его спас врач.")
                else:
                    sub_client.kick(chatId=activity_games[communityid]["initial_chat"], allowRejoin=True, userId=top)
                    activity_games[communityid]['users'].pop(top)
                buffer_game[communityid]["golosa"] = {}
                buffer_game[communityid]["accept_mafia"] = buffer_game[communityid]["mafia"]
                activity_games[communityid]["times"] = "day"

                sub_client.edit_chat(viewOnly=False, chatId=activity_games[communityid]["initial_chat"])
                sub_client.send_message(chatId=activity_games[communityid]["initial_chat"], file=day, fileType="gif")
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"Солнце всходит, подсушивая на тротуарах пролитую ночью кровь...")

            elif buffer_game[communityid]["accept"] == []:
                top = sorted(list(buffer_game[communityid]["golosa"].keys()))[::-1][:1]
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"Линчевали игрока, что оказался {activity_games[communityid]['users'][top]}")
                sub_client.kick(chatId=activity_games[communityid]["initial_chat"], allowRejoin=True, userId=top)
                activity_games[communityid]['users'].remove(top)
                activity_games[communityid]['day']+=1
                buffer_game[communityid]["golosa"] = {}

                buffer_game[communityid]["accept"] = buffer_game[communityid]["all_role_in_game"]
                activity_games[communityid]["times"] = "night"
                sub_client.send_message(chatId=activity_games[communityid]["initial_chat"], file=night, fileType="gif")
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message=f"Ночь {activity_games[communityid]['day']}\nНа улицы города выходят лишь самые отважные и бесстрашные. Утром попробуем сосчитать их головы...")
                sub_client.edit_chat(viewOnly=True, chatId=activity_games[communityid]["initial_chat"])

            elif buffer_game[communityid]["heal"] != "":
                sub_client.send_web_message(chatId=activity_games[communityid]["initial_chat"], message="Врач выбрал, кого будет лечить.")

def treatment(obj, data):
    Thread(target=on_message, args=(json.loads(data)['o'], )).start()

def error(sockets, text):
    print(f"\n\n\n{text}")
    sockets.close()

def start_socket():
     while True:
        try:
            headers = {
                "NDCDEVICEID": client.device_id,
                "NDCAUTH": client.sid}
            
            milliseconds = int(time.time() * 1000)
            data = f"{client.device_id}|{milliseconds}"
            signature = aminofix.lib.util.signature

            headers["NDC-MSG-SIG"] = signature(data)
            socket = websocket.WebSocketApp(
                f"wss://ws1.narvii.com/?signbody={client.device_id}%7C{milliseconds}",
                on_message = treatment,
                header = headers,
                on_error=error)
            Thread(target = socket.run_forever, kwargs = {"ping_interval": 60}).start()
        except Exception as e:
            print(e)

        time.sleep(60)
        socket.close()

Thread(target=start_socket).start()