import requests
from urllib import parse
import json
import pandas as pd
from urllib.request import urlopen

champion_df = pd.read_csv('./00. data/champions.csv', index_col = 0)
item_df = pd.read_csv('./00. data/items.csv', index_col = 0)
spell_df = pd.read_csv('./00. data/spell.csv', index_col = 0)


def headers(): # api_key로 header불러오기
    key_fd = open('./keys/api_key.txt', mode='r')
    api_key = key_fd.read(100)
    key_fd.close()
    request_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": api_key  #Riot API 키   
    }
    return request_headers
headers = headers()
def check_version():
    response = urlopen("https://ddragon.leagueoflegends.com/api/versions.json").read().decode('utf-8')
    version_data = json.loads(response)
    return version_data[0]

version = check_version()
def new_datas() : # 새버전의 데이터 불러오기(챔피언, 아이템, 스펠, 룬)
    # 챔피언 데이터
    response = urlopen(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json").read().decode('utf-8')
    champion_data = json.loads(response)
    cham_list = list(champion_data['data'])
    # 아이템 데이터
    response = urlopen(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/item.json").read().decode('utf-8')
    item_data = json.loads(response)
    itemKey_list = list(item_data['data'])
    # 스펠 데이터
    response = urlopen(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/summoner.json").read().decode('utf-8')
    spell_data = json.loads(response)
    # 룬 데이터
    response = urlopen(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/runesReforged.json").read().decode('utf-8')
    rune_data = json.loads(response)
    name_list = []
    chams_list = []
    key_list = []
    tags_list = []
    for cham in cham_list:
        name = champion_data['data'][cham]['name']
        key = champion_data['data'][cham]['key']
        tags = champion_data['data'][cham]['tags']
        tags = ', '.join(tags)
        chams_list.append(cham)
        name_list.append(name)
        key_list.append(key)
        tags_list.append(tags)
    champion_df = pd.DataFrame({
        'name' : name_list,
        'key' : key_list,
        'tags' : tags_list,
        'eng_name' : cham_list
    })
    name_list = []
    gold_list = []
    tags_list = []
    for item in itemKey_list:
        name = item_data['data'][item]['name']
        gold = item_data['data'][item]['gold']['total']
        tags = item_data['data'][item]['tags']
        tags = ', '.join(tags)
        name_list.append(name)
        gold_list.append(gold)
        tags_list.append(tags)

    item_df = pd.DataFrame({
    'name' : name_list,
    'key' : itemKey_list,
    'gold' : gold_list,
    'tags' : tags_list,
    })
    
    spell_names = []
    spell_descriptions = []
    spell_keys = []
    spells = []
    for spell in spell_data['data']:
        spell_name = spell_data['data'][spell]['name']
        spell_description = spell_data['data'][spell]['description']
        spell_key = spell_data['data'][spell]['key']
        if spell == 'SummonerSmite' :
            spell_description = spell_description.replace('@SmiteBaseDamage@의','') # 수치 제거
        spell_names.append(spell_name)
        spell_descriptions.append(spell_description)
        spell_keys.append(spell_key)
        spells.append(spell)
    
    spell_df = pd.DataFrame({
    'name' : spell_names,
    'description' : spell_descriptions,
    'key' : spell_keys,
    'eng' : spells
    })
    
    name_list, key_list =[], []
    for i in range(5):
        rune_name = rune_data[i]['name']
        rune_key = rune_data[i]['id']
        name_list.append(rune_name)
        key_list.append(rune_key)
        for k in range(4):
            rune_len = len(rune_data[i]['slots'][k]['runes'])
            for l in range(rune_len):
                rune_name = rune_data[i]['slots'][k]['runes'][l]['name']
                rune_key = rune_data[i]['slots'][k]['runes'][l]['id']
                name_list.append(rune_name)
                key_list.append(rune_key)
    sub_names = ['체력 + 15~90(레벨에 비례)', '방어력 + 9', '마법저항력 + 8', '공격속도 + 10%', '스킬가속 + 8', '적응형 능력치 + 9']
    sub_keys = [5001, 5002, 5003, 5005, 5007, 5008]
    for i in range(6):
        name_list.append(sub_names[i])
        key_list.append(sub_keys[i])
    rune_df = pd.DataFrame({
    'name' : name_list,
    'key' : key_list,
    })
    
    champion_df.to_csv('./00. data/champions.csv')
    item_df.to_csv('./00. data/items.csv')
    spell_df.to_csv('./00. data/spell.csv')
    rune_df.to_csv('./00. data/runes.csv')

    return champion_df, item_df, spell_df, rune_df

def searchUserId(nickname) : # 유저의 암호화된 아이디를 불러오는 함수 유저의 암호화된 아이디를 불러오는 함수
        user_data = requests.get("https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + parse.quote(nickname), headers=headers).json()
        userId = user_data['id']
        userAccountId = user_data['accountId']
        userPuuid = user_data['puuid']
        nickname = user_data['name']
        userLevel = user_data['summonerLevel']
        return userId, userAccountId, userPuuid, nickname, userLevel

def searchChampMatchId(accountId, champion): # 한유저의 특정 챔피언 매치ID들을 불러오는 함수
    championKey = champion_df['key'][champion_df['key'][champion_df['name'] == champion].index[0]] # 챔피언 키구하기
    match_data = requests.get("https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accountId + "?champion=" + str(championKey)  + '&queue=420',headers=headers).json()['matches']
    match_list = []
    for i in range(len(match_data)):
        match = match_data[i]['gameId']
        match_list.append(match)
    return match_list
# 한유저의 매치 ID들을 불러오는 함수
def searchMatchId(accountId):
    match_data = requests.get("https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accountId  + '?queue=420' ,headers=headers).json()['matches']
    match_list = []
    for i in range(len(match_data)):
        match = match_data[i]['gameId']
        match_list.append(match)
    return match_list
# 챔피언키로 챔피언 이름 불러오는 함수
def searchChampion(championKey):
    champ = champion_df['name'][champion_df['name'][champion_df['key'] == championKey].index[0]]
    return champ  
# 아이템키로 아이템 이름 불러오는 함수
def searchItem(itemKey):
    item = item_df['name'][item_df['name'][item_df['key'] == itemKey].index[0]]
    return item 
# 스펠키로 아이템 이름 불러오는 함수
def searchSpell(spellKey):
    spell = spell_df['name'][spell_df['name'][spell_df['key'] == spellKey].index[0]]
    return spell 
# 한 매치의결과창을 불러오는 함수
def match_record(matchId):
    match_record = requests.get('https://kr.api.riotgames.com/lol/match/v4/matches/' + str(matchId), headers=headers).json()
    users_record = match_record['participants']
    users_info = match_record['participantIdentities']
    user_list = []
    for user_info in users_info:
        user_name = user_info['player']['summonerName']
        user_list.append(user_name)
    users_champion = []
    users_kda = []
    users_items = []
    users_spell = []
    users_lane = []
    users_ornament =[]
    users_win =[]
    for user_record in users_record:
        user_champion = searchChampion(user_record['championId'])
        user_kda = str(user_record['stats']['kills']) + '/' + str(user_record['stats']['deaths']) + '/' + str(user_record['stats']['assists'])
        user_items = []
        for i in range(6):
            itemKey = user_record['stats']['item'+str(i)]
            if itemKey == 0:
                pass
            else:
                user_items.append(searchItem(user_record['stats']['item'+str(i)]))
        user_ornament = searchItem(user_record['stats']['item6'])
        user_items = ', '.join(user_items)
        user_spell = [searchSpell(user_record['spell1Id']), searchSpell(user_record['spell2Id'])]
        user_spell = ', '.join(user_spell)
        user_lane = user_record['timeline']['lane']
        user_win = user_record['stats']['win']
        if user_win == True:
            user_win = '승리'
        else :
            user_win = '패배'
        users_champion.append(user_champion)
        users_kda.append(user_kda)
        users_items.append(user_items)
        users_ornament.append(user_ornament)
        users_spell.append(user_spell)
        users_lane.append(user_lane)
        users_win.append(user_win)
    df = pd.DataFrame({
    'nickname' : user_list,
    'champion' : users_champion,
    'spell' : users_spell,
    'lane' : users_lane,
    'kda' : users_kda,
    'result_items' : users_items,
    'ornament' : users_ornament,
    'result' : users_win
    })
    # 트롤링 추가
    df['trolling'] = df.apply(lambda r : True if str(r.result_items) == '' or str(r.result_items.split(', ')[0]) == str(r.result_items.split(', ')[-1]) else False, axis=1)
    return df
# 유저 인덱스 구하기
def userIndex(user, users_info):
    user_list = []
    for user_info in users_info:
        user_name = user_info['player']['summonerName']
        user_list.append(user_name)
    user_index = user_list.index(user)
    return user_index
# 한 유저의 최근 매치 결과를 불러오는 함수

def userMatches_record(user, number):
    userId, accountId, userPuuid = searchUserId(user)
    match_list = searchMatchId(accountId)[:number] # nuber = 원하는 매치의 수
    users_champion = []
    users_kda = []
    users_items = []
    users_spell = []
    users_lane = []
    users_ornament =[]
    users_win =[]
    for match in match_list:
        match_info = requests.get('https://kr.api.riotgames.com/lol/match/v4/matches/' + str(match), headers=headers).json()
        users_info = match_info['participantIdentities']
        
        user_index = userIndex(user, users_info)
        user_record = match_info['participants'][user_index]
        user_champion = searchChampion(user_record['championId'])
        user_kda = str(user_record['stats']['kills']) + '/' + str(user_record['stats']['deaths']) + '/' + str(user_record['stats']['assists'])
        user_items = []
        for i in range(6):
            itemKey = user_record['stats']['item'+str(i)]
            if itemKey == 0:
                pass
            else:
                user_items.append(searchItem(user_record['stats']['item'+str(i)]))
        user_ornament = searchItem(user_record['stats']['item6'])
        user_items = ', '.join(user_items)
        user_spell = [searchSpell(user_record['spell1Id']), searchSpell(user_record['spell2Id'])]
        user_spell = ', '.join(user_spell)
        user_lane = user_record['timeline']['lane']
        user_win = user_record['stats']['win']
        if user_win == True: 
            user_win = '승리'
        else :
            user_win = '패배'
        users_champion.append(user_champion)
        users_kda.append(user_kda)
        users_items.append(user_items)
        users_ornament.append(user_ornament)
        users_spell.append(user_spell)
        users_lane.append(user_lane)
        users_win.append(user_win)
        
    df = pd.DataFrame({
    'nickname' : user,
    'champion' : users_champion,
    'spell' : users_spell,
    'lane' : users_lane,
    'kda' : users_kda,
    'result_items' : users_items,
    'ornament' : users_ornament,
    'result' : users_win
    })
    df['trolling'] = df.apply(lambda r : True if str(r.result_items) == '' or str(r.result_items.split(', ')[0]) == str(r.result_items.split(', ')[-1]) else False, axis=1)
    
    return df


# 최근 유저의 전적을 정리 하는 함수 
def recentHistory(df):
    winningRate = str(round(df['result'].value_counts()['승리']/ len(df) * 100)) + '%'
    mostChampion = ', '.join(df['champion'].value_counts().index[:5])
    mostLane = ', '.join(df['lane'].value_counts().index[:2])
    if df['trolling'].value_counts()[True] == 0:
        trolling = '0%'
    else :
        trolling = str(round(df['trolling'].value_counts()[True]/ len(df) * 100)) + '%'
    recentHistory = f'최근승률 : {winningRate}, 최근 가장 많이 사용한 챔피언 : {mostChampion}, 최근 주 라인 : {mostLane}, 최근 트롤링 빈도 : {trolling}'
    return recentHistory
