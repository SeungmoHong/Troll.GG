import requests
from urllib import parse
import json
import pandas as pd
from urllib.request import urlopen

champion_df = pd.read_csv('../00. data/champions.csv', index_col = 0)
item_df = pd.read_csv('../00. data/items.csv', index_col = 0)


def riot_api(): # api_key로 header불러오기
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

def new_datas(version) : # 새버전의 데이터 불러오기(챔피언, 아이템)
    # 챔피언 데이터
    response = urlopen(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json").read().decode('utf-8')
    champion_data = json.loads(response)
    cham_list = list(champion_data['data'])
    # 아이템 데이터
    response = urlopen(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/item.json").read().decode('utf-8')
    item_data = json.loads(response)
    itemKey_list = list(item_data['data'])
    name_list = []
    key_list = []
    tags_list = []
    for cham in cham_list:
        name = champion_data['data'][cham]['name']
        key = champion_data['data'][cham]['key']
        tags = champion_data['data'][cham]['tags']
        tags = ', '.join(tags)
        name_list.append(name)
        key_list.append(key)
        tags_list.append(tags)
    champion_df = pd.DataFrame({
        'name' : name_list,
        'key' : key_list,
        'tags' : tags_list,
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
    champion_df.to_csv('../00. data/champions.csv')
    item_df.to_csv('../00. data/items.csv')

    return champion_df, item_df

def searchUserId(headers, nickname) : # 유저의 암호화된 아이디를 불러오는 함수 유저의 암호화된 아이디를 불러오는 함수
        user_data = requests.get("https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + parse.quote(nickname), headers=headers).json()
        userId = user_data['id']
        userAccountId = user_data['accountId']
        userPuuid = user_data['puuid'] 
        return userId, userAccountId, userPuuid

def searchChampMatchId(headers, accountId, champion): # 한유저의 특정 챔피언 매치ID들을 불러오는 함수
    championKey = champion_df['key'][champion_df['key'][champion_df['name'] == champion].index[0]] # 챔피언 키구하기
    match_data = requests.get("https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accountId + "?champion=" + str(championKey),headers=headers).json()['matches']
    match_list = []
    for i in range(len(match_data)):
        match = match_data[i]['gameId']
        match_list.append(match)
    return match_list
# 한유저의 매치 ID들을 불러오는 함수
def searchMatchId(headers,accountId):
    match_data = requests.get("https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" + accountId,headers=headers).json()['matches']
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