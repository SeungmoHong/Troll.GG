import requests
from urllib import parse
import json
import pandas as pd
from urllib.request import urlopen

champion_df = pd.read_csv('../00. data/champions.csv', index_col = 0)
item_df = pd.read_csv('../00. data/items.csv', index_col = 0)
spell_df = pd.read_csv('../00. data/spell.csv', index_col = 0)
rune_df = pd.read_csv('../00. data/runes.csv', index_col = 0)


def headers(): # api_key로 header불러오기
    key_fd = open('../keys/api_key.txt', mode='r')
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
    
    champion_df.to_csv('../00. data/champions.csv')
    item_df.to_csv('../00. data/items.csv')
    spell_df.to_csv('../00. data/spell.csv')
    rune_df.to_csv('../00. data/runes.csv')

    return champion_df, item_df, spell_df, rune_df

def searchUserId(nickname) : # 유저의 암호화된 아이디를 불러오는 함수 유저의 암호화된 아이디와 정보를 불러오는 함수
        user_data = requests.get("https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + parse.quote(nickname), headers=headers).json()
        userId = user_data['id']
        userAccountId = user_data['accountId']
        userPuuid = user_data['puuid']
        nickname = user_data['name']
        userLevel = user_data['summonerLevel']
        profileIconId = user_data['profileIconId']
        return userId, userAccountId, userPuuid, nickname, userLevel, profileIconId

def userInfo(id): # 유저의 랭크티어와 승,패 정보를 받아오는 함수
    user_data = requests.get('https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/'+ parse.quote(id), headers=headers).json()
    if user_data[0]['queueType'] == 'RANKED_SOLO_5x5':
        num = 0
    else:
        num = 1

    tier = user_data[num]['tier']
    rank = user_data[num]['rank']
    wins = user_data[num]['wins']
    losses = user_data[num]['losses']
    point = user_data[num]['leaguePoints']

    return tier, rank, wins, losses, point



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
# 챔피언키로 챔피언 영문이름을 불러오는 함수
def searchChampion(championKey):
    champ = champion_df['eng_name'][champion_df['eng_name'][champion_df['key'] == championKey].index[0]]
    return champ  
# 영문 챔피언 이름으로 챔피언 이름을 불러오는 함수
def translationChampion(championKey):
    champ = champion_df['name'][champion_df['name'][champion_df['eng_name'] == championKey].index[0]]
    return champ  
# 아이템키로 아이템 이름 불러오는 함수
def searchItem(itemKey):
    item = item_df['name'][item_df['name'][item_df['key'] == itemKey].index[0]]
    return item 
# 스펠키로 스펠 이름 불러오는 함수
def searchSpell(spellKey):
    spell = spell_df['name'][spell_df['name'][spell_df['key'] == spellKey].index[0]]
    return spell
# 스펠 영문이름으로 스펠 이름 불러오는 함수
def translationSpell(eng):
    spell = spell_df['name'][spell_df['name'][spell_df['eng'] == eng].index[0]]
    return spell
# 스펠키로 스펠 영문 이름 불러오는 함수
def searchEngSpell(spellKey):
    spell = spell_df['eng'][spell_df['eng'][spell_df['key'] == spellKey].index[0]]
    return spell
# 한 매치의결과창을 불러오는 함수 현재 사용안함
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
# 매치의 플레이시간을 불러오는 함수
def playingTime(matchId):
    match_data = requests.get('https://kr.api.riotgames.com/lol/match/v4/timelines/by-match/' + str(matchId), headers=headers).json()
    playingTime = round(match_data['frames'][-1]['timestamp'] / 60000)

    return playingTime
# 한 유저의 최근 매치 결과를 불러오는 함수 사용중

def userMatches_record(user):
    userId, userAccountId, userPuuid, nickname, userLevel, profileIconId = searchUserId(user)
    match_list = searchMatchId(userAccountId)[:30] 
    users_champion = []
    all_champions = []
    users_kda = []
    users_items = []
    users_spell = []
    users_runes = []
    users_lane = []
    users_ornament =[]
    users_win =[]
    users_gold = []
    users_level = []
    users_cs = []
    users_visionWardsBoughtInGame =[]
    users_wardsPlaced = []
    users_wardsKilled = []
    users_trolling = []

    #users_playingTimes = [] #시간이 너무 오래걸려서 생략

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
                user_items.append('0')
            else:
                user_items.append(str(itemKey) + '.png')
        champion_list = []
        for i in range(10):
            champId = match_info['participants'][i]['championId']
            champion_list.append(champId)
        champion_list = [searchChampion(champ) for champ in champion_list]          
        if user_record['stats']['item6'] == 0:
            user_ornament = '0'
        else:
            user_ornament = str(user_record['stats']['item6']) + '.png'
        user_spell = [searchEngSpell(user_record['spell1Id']), searchEngSpell(user_record['spell2Id'])]
        user_runes = [str(user_record['stats']['perkPrimaryStyle']) + '.png', str(user_record['stats']['perkSubStyle']) + '.png']
        user_lane = user_record['timeline']['lane']
        user_win = user_record['stats']['win']
        if user_win == True: 
            user_win = '승'
        else :
            user_win = '패'
        user_gold = user_record['stats']['goldEarned']
        user_level = user_record['stats']['champLevel']
        user_cs = user_record['stats']['totalMinionsKilled'] + user_record['stats']['neutralMinionsKilled']
        user_visionWardsBoughtInGame = user_record['stats']['visionWardsBoughtInGame']
        user_wardsPlaced = user_record['stats']['wardsPlaced']
        user_wardsKilled = user_record['stats']['wardsKilled']
        # user_playingTime = playingTime(match) #시간이 너무 오래걸려서 생략
        if user_items.count(0) == 6 or user_items.count(user_items[0]) == 6:
            user_trolling = True
        else:
            user_trolling = False
        


        users_champion.append(user_champion)
        all_champions.append(champion_list)
        users_kda.append(user_kda)
        users_items.append(user_items)
        users_ornament.append(user_ornament)
        users_spell.append(user_spell)
        users_runes.append(user_runes)
        users_lane.append(user_lane)
        users_win.append(user_win)
        users_gold.append(user_gold)
        users_level.append(user_level)
        users_cs.append(user_cs)
        users_visionWardsBoughtInGame.append(user_visionWardsBoughtInGame)
        users_wardsPlaced.append(user_wardsPlaced)
        users_wardsKilled.append(user_wardsKilled)
        users_trolling.append(user_trolling)
        #users_playingTimes.append(user_playingTime) #시간이 너무 오래걸려서 생략

    

    result = {
    'champion' : users_champion,
    'all_champions' : all_champions,
    'spell' : users_spell,
    'runes' : users_runes,
    'lane' : users_lane,
    'gold' : users_gold,
    'level' : users_level,
    'cs' : users_cs,
    'visionWardsBoughtInGame': users_visionWardsBoughtInGame,
    'wardsPlaced' : users_wardsPlaced,
    'wardsKilled' : users_wardsKilled,
    'kda' : users_kda,
    'result_items' : users_items,
    'ornament' : users_ornament,
    #'playingTime' : users_playingTimes,
    'trolling' : users_trolling,
    'result' : users_win
    }
        

    # df['trolling'] = df.apply(lambda r : True if str(r.result_items) == '' or str(r.result_items.split(', ')[0]) == str(r.result_items.split(', ')[-1]) else False, axis=1)
    
        
    return result


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
