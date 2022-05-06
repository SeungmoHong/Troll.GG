import requests
from urllib import parse
import json
import pandas as pd
import re
import math
from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime

champion_df = pd.read_csv('../00. data/champions.csv', index_col=0)
champion_df['lower_name'] = champion_df['eng_name'].apply(
    lambda r: r.lower())  # OP.GG의 챔피언 찾기를 위해 소문자화
item_df = pd.read_csv('../00. data/items.csv', index_col=0)
spell_df = pd.read_csv('../00. data/spell.csv', index_col=0)
rune_df = pd.read_csv('../00. data/runes.csv', index_col=0)


def headers():  # api_key로 header불러오기
    key_fd = open('../keys/api_key.txt', mode='r')
    api_key = key_fd.read(100)
    key_fd.close()
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com",
        "X-Riot-Token": api_key  # Riot API 키
    }
    return request_headers


headers = headers()


def check_version():
    response = urlopen(
        "https://ddragon.leagueoflegends.com/api/versions.json").read().decode('utf-8')
    version_data = json.loads(response)
    return version_data[0]


version = check_version()


def new_datas():  # 새버전의 데이터 불러오기(챔피언, 아이템, 스펠, 룬)
    # 챔피언 데이터
    response = urlopen(
        f"http://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/champion.json").read().decode('utf-8')
    champion_data = json.loads(response)
    cham_list = list(champion_data['data'])
    # 아이템 데이터
    response = urlopen(
        f"http://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/item.json").read().decode('utf-8')
    item_data = json.loads(response)
    itemKey_list = list(item_data['data'])
    # 스펠 데이터
    response = urlopen(
        f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/summoner.json").read().decode('utf-8')
    spell_data = json.loads(response)
    # 룬 데이터
    response = urlopen(
        f"https://ddragon.leagueoflegends.com/cdn/{version}/data/ko_KR/runesReforged.json").read().decode('utf-8')
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
        'name': name_list,
        'key': key_list,
        'tags': tags_list,
        'eng_name': cham_list
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
        'name': name_list,
        'key': itemKey_list,
        'gold': gold_list,
        'tags': tags_list,
    })
    spell_names = []
    spell_descriptions = []
    spell_keys = []
    spells = []
    for spell in spell_data['data']:
        spell_name = spell_data['data'][spell]['name']
        spell_description = spell_data['data'][spell]['description']
        spell_key = spell_data['data'][spell]['key']
        if spell == 'SummonerSmite':
            spell_description = spell_description.replace(
                '@SmiteBaseDamage@의', '')  # 수치 제거
        spell_names.append(spell_name)
        spell_descriptions.append(spell_description)
        spell_keys.append(spell_key)
        spells.append(spell)

    spell_df = pd.DataFrame({
        'name': spell_names,
        'description': spell_descriptions,
        'key': spell_keys,
        'eng': spells
    })
    name_list, key_list = [], []
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
    sub_names = ['체력 + 15~90(레벨에 비례)', '방어력 + 9', '마법저항력 + 8',
                 '공격속도 + 10%', '스킬가속 + 8', '적응형 능력치 + 9']
    sub_keys = [5001, 5002, 5003, 5005, 5007, 5008]
    for i in range(6):
        name_list.append(sub_names[i])
        key_list.append(sub_keys[i])
    rune_df = pd.DataFrame({
        'name': name_list,
        'key': key_list,
    })
    champion_df.to_csv('../00. data/champions.csv')
    item_df.to_csv('../00. data/items.csv')
    spell_df.to_csv('../00. data/spell.csv')
    rune_df.to_csv('../00. data/runes.csv')

    return champion_df, item_df, spell_df, rune_df


def searchUserId(nickname):  # 유저의 암호화된 아이디를 불러오는 함수 유저의 암호화된 아이디와 정보를 불러오는 함수
    user_data = requests.get("https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" +
                             parse.quote(nickname), headers=headers).json()
    userId = user_data['id']
    userAccountId = user_data['accountId']
    userPuuid = user_data['puuid']
    nickname = user_data['name']
    userLevel = user_data['summonerLevel']
    profileIconId = user_data['profileIconId']
    return userId, userAccountId, userPuuid, nickname, userLevel, profileIconId


def userInfo(id):  # 유저의 랭크티어와 승,패 정보를 받아오는 함수
    user_data = requests.get(
        'https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/' + parse.quote(id), headers=headers).json()
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


def searchChampMatchId(accountId, champion):  # 한유저의 특정 챔피언 매치ID들을 불러오는 함수
    championKey = champion_df['key'][champion_df['key']
                                     [champion_df['name'] == champion].index[0]]  # 챔피언 키구하기
    match_data = requests.get("https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/" +
                              accountId + "?champion=" + str(championKey) + '&queue=420', headers=headers).json()['matches']
    match_list = []
    for i in range(len(match_data)):
        match = match_data[i]['gameId']
        match_list.append(match)
    return match_list
# 한유저의 매치 ID들을 불러오는 함수


def searchMatchId(puuId):
    match_list = requests.get(
        f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuId}/ids?queue=420&type=ranked&start=0&count=100", headers=headers).json()
    return match_list
# 챔피언키로 챔피언 영문이름을 불러오는 함수


def searchChampion(championKey):
    champ = champion_df['eng_name'][champion_df['eng_name']
                                    [champion_df['key'] == championKey].index[0]]
    return champ
# 영문 챔피언 이름으로 챔피언 이름을 불러오는 함수


def translationChampion(eng):
    champ = champion_df['name'][champion_df['name']
                                [champion_df['eng_name'] == eng].index[0]]

    return champ
# 챔피언 이름으로 영문 챔피언 이름을 불러오는 함수


def translationChampion2(kor):
    champ = champion_df['eng_name'][champion_df['eng_name']
                                    [champion_df['name'] == kor].index[0]]
    return champ
# 아이템키로 아이템 이름 불러오는 함수


def searchItem(itemKey):
    if itemKey == 7013:
        itemKey = 6655
    item = item_df['name'][item_df['name'][item_df['key'] == itemKey].index[0]]
    return item
# 스펠키로 스펠 이름 불러오는 함수


def searchSpell(spellKey):
    spell = spell_df['name'][spell_df['name']
                             [spell_df['key'] == spellKey].index[0]]
    return spell
# 스펠 영문이름으로 스펠 이름 불러오는 함수


def translationSpell(eng):
    spell = spell_df['name'][spell_df['name'][spell_df['eng'] == eng].index[0]]
    return spell
# 스펠키로 스펠 영문 이름 불러오는 함수


def searchEngSpell(spellKey):
    spell = spell_df['eng'][spell_df['eng']
                            [spell_df['key'] == spellKey].index[0]]
    return spell


# 매치의 플레이시간 계산해주는 함수
def playingTime(playingTime):
    tmp = datetime.timedelta(milliseconds=playingTime)
    total_time = str(tmp).split(':')
    if total_time[0] == '0':
        time = f'{total_time[1]}분 {total_time[2].split(".")[0]}초'
    else:
        time = f'{total_time[0]}시간 {total_time[1]}분 {total_time[2].split(".")[0]}초'

    return time

# 밀리세컨드단위의 시간을 날짜로 계산하는 함수


def date_rocord(timestamp):
    tmp = datetime.datetime(1970, 1, 1)
    date_rocord = tmp - datetime.timedelta(milliseconds=-timestamp, hours=-9)

    return str(date_rocord.date())

# 한 유저의 최근 매치 결과를 불러오는 함수


def userMatches_record(user):
    userId, userAccountId, userPuuid, nickname, userLevel, profileIconId = searchUserId(
        user)
    match_list = searchMatchId(userPuuid)[:30]
    users_champion = []
    all_champions = []
    users_kda = []
    users_items = []
    users_spell = []
    users_runes = []
    users_lane = []
    users_ornament = []
    users_win = []
    users_gold = []
    users_level = []
    users_cs = []
    users_visionWardsBoughtInGame = []
    users_wardsPlaced = []
    users_wardsKilled = []
    playing_times = []
    matches_timestamp = []

    for matchId in match_list:
        match_record = requests.get(
            'https://asia.api.riotgames.com/lol/match/v5/matches/' + str(matchId), headers=headers).json()
        for i in range(10):
            if match_record['info']['participants'][i]['summonerName'] == nickname:
                userIndex = i
                break
        user_data = match_record['info']['participants'][userIndex]
        user_champion = user_data['championName']
        user_kda = str(user_data['kills']) + '/' + \
            str(user_data['deaths']) + '/' + str(user_data['assists'])
        user_items = []
        for i in range(6):
            itemKey = user_data['item'+str(i)]
            if itemKey == 0:
                user_items.append('0')
            elif itemKey == 7013:
                user_items.append('6655' + '.png')
            else:
                user_items.append(str(itemKey) + '.png')
        champion_list = []
        for i in range(10):
            champId = match_record['info']['participants'][i]['championId']
            champion_list.append(champId)
        champion_list = [searchChampion(champ) for champ in champion_list]
        if user_data['item6'] == 0:
            user_ornament = '0'
        else:
            user_ornament = str(user_data['item6']) + '.png'
        user_spell = [searchEngSpell(user_data['summoner1Id']), searchEngSpell(
            user_data['summoner2Id'])]
        user_runes = [str(user_data['perks']['styles'][0]['style']) +
                      '.png', str(user_data['perks']['styles'][1]['style']) + '.png']
        user_lane = user_data['teamPosition']
        user_win = user_data['win']
        if user_win == True:
            user_win = '승'
        else:
            user_win = '패'
        user_gold = user_data['goldEarned']
        user_level = user_data['champLevel']
        user_cs = user_data['totalMinionsKilled']
        user_visionWardsBoughtInGame = user_data['visionWardsBoughtInGame']
        user_wardsPlaced = user_data['wardsPlaced']
        user_wardsKilled = user_data['wardsKilled']

        time_stamp = requests.get(
            f'https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}/timeline', headers=headers).json()['info']['frames'][-1]['timestamp']
        playing_time = playingTime(time_stamp)

        match_timestamp = date_rocord(
            match_record['info']['gameStartTimestamp'])

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
        playing_times.append(playing_time)
        matches_timestamp.append(match_timestamp)

        # 상세정보

        # match_result = {
        #     'all_championsId': [match_record['info']['participants'][i]['championId'] for i in range(10)],
        #     'summonerNames': [match_record['info']['participants'][i]['summonerName'] for i in range(10)],
        #     'spells': [[match_record['info']['participants'][i]['summoner1Id'], match_record['info']['participants'][i]['summoner2Id']] for i in range(10)],
        #     'kda': [str(match_record['info']['participants'][i]['kills']) + '/' +
        #             str(match_record['info']['participants'][i]['deaths']) + '/' + str(match_record['info']['participants'][i]['assists']) for i in range(10)],
        #     'items': [[match_record['info']['participants'][i][f'item{k}'] for k in range(6)] for i in range(10)],
        #     'ornaments': [match_record['info']['participants'][i]['item6'] for i in range(10)],
        #     'runes': [[match_record['info']['participants'][i]['perks']['styles'][0]['style'],
        #                match_record['info']['participants'][i]['perks']['styles'][1]['style']] for i in range(10)],
        #     'level': [match_record['info']['participants'][i]['champLevel'] for i in range(10)],
        #     'gold': [match_record['info']['participants'][i]['goldEarned'] for i in range(10)],
        #     'cs': [match_record['info']['participants'][i]['totalMinionsKilled'] for i in range(10)],
        #     'visionWardsBoughtInGame': [match_record['info']['participants'][i]['visionWardsBoughtInGame'] for i in range(10)],
        #     'wardsPlaced': [match_record['info']['participants'][i]['wardsPlaced'] for i in range(10)],
        #     'user_wardsKilled': [match_record['info']['participants'][i]['wardsKilled'] for i in range(10)]
        # }
        # match_results.append(match_result)

    # 포지션 한국어로
    kor_usersLane = []
    for lane in users_lane:
        if lane == 'TOP':
            kor_lane = '탑'
        elif lane == 'JUNGLE':
            kor_lane = '정글'
        elif lane == 'MIDDLE':
            kor_lane = '미드'
        elif lane == 'BOTTOM':
            kor_lane = '원딜'
        elif lane == 'UTILITY':
            kor_lane = '서포터'
        else:
            kor_lane = lane
        kor_usersLane.append(kor_lane)
    result = {
        'champion': users_champion,
        'all_champions': all_champions,
        'spell': users_spell,
        'runes': users_runes,
        'kor_lane': kor_usersLane,
        'lane': users_lane,
        'gold': users_gold,
        'level': users_level,
        'cs': users_cs,
        'visionWardsBoughtInGame': users_visionWardsBoughtInGame,
        'wardsPlaced': users_wardsPlaced,
        'wardsKilled': users_wardsKilled,
        'kda': users_kda,
        'result_items': users_items,
        'ornament': users_ornament,
        'playingTime': playing_times,
        'gameStartTimestamp': matches_timestamp,
        'result': users_win,
        'match_Id': match_list,
    }

    return result


# 최근 유저의 전적을 정리 하는 함수
def recentHistory(df):
    winningRate = str(round(df['result'].value_counts()[
                      '승리'] / len(df) * 100)) + '%'
    mostChampion = ', '.join(df['champion'].value_counts().index[:5])
    mostLane = ', '.join(df['lane'].value_counts().index[:2])
    if df['trolling'].value_counts()[True] == 0:
        trolling = '0%'
    else:
        trolling = str(round(df['trolling'].value_counts()[
                       True] / len(df) * 100)) + '%'
    recentHistory = f'최근승률 : {winningRate}, 최근 가장 많이 사용한 챔피언 : {mostChampion}, 최근 주 라인 : {mostLane}, 최근 트롤링 빈도 : {trolling}'
    return recentHistory


# OP.GG 크롤링 ///


# 챔피언의 영문이름을 한글로 바꿔주는 함수
def translation_champion(eng):
    try:
        if eng == 'Wukong':
            champion = '오공'
        elif eng == 'Nunu & Willump' or eng == 'Nunu &amp; Willump':
            champion = '누누와 윌럼프'
        else:
            eng = eng.lower().replace(' ', '').replace('.', '')
            champion = champion_df['name'][champion_df['name']
                                           [champion_df['lower_name'] == eng].index[0]]
    except:
        champion = eng
    return champion
# 태그 지우는 함수


def removeTags(strings):
    strings = re.sub('<.+?>', '', str(strings),
                     0).strip().replace('[', '').replace(']', '')
    return strings

# OP.GG 아이템이미지의 키를 구하는 함수 + 룬


def findItem(itemLink):
    items = re.findall(r'\d\d\d\d.png', str(itemLink))
    items = [item.strip('.png') for item in items]

    return items

# OP.GG 스킬이미지의 영문 이름을 구하는 함수


def findSkill(link):
    name = re.findall(r'spell/.*png', str(link))
    name = ''.join(name).strip('spell/').strip('.png')
    return name


# 라인별 티어리스트를 가져오는 함수
def tier_list():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://www.op.gg/champion/statistics'
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    lanes = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
    champion_dict = {}
    winRate_dict = {}
    pickRate_dict = {}
    tier_dict = {}
    for lane in lanes:
        tmp = soup.find(attrs={'class': f'tabItem champion-trend-tier-{lane}'})
        champion_tags = tmp.select('.champion-index-table__name')
        champion_list = removeTags(champion_tags).replace("'", '')
        champion_list = champion_list.split(', ')
        kor_champions = [translation_champion(
            champ) for champ in champion_list]

        winRate_list = []
        pickRate_list = []
        tiers_list = []
        for i in range(len(tmp.find_all('tr'))):
            tags = tmp.find_all('tr')[i].select(
                '.champion-index-table__cell.champion-index-table__cell--value')
            winRate = removeTags(tags).split(', ')[0]
            pickRate = removeTags(tags).split(', ')[1]
            tier = tags[2].find('img').attrs['src'][-5]
            winRate_list.append(winRate)
            pickRate_list.append(pickRate)
            tiers_list.append(tier)

        champion_dict[lane] = kor_champions
        winRate_dict[lane] = winRate_list
        pickRate_dict[lane] = pickRate_list
        tier_dict[lane] = tiers_list
    return champion_dict, winRate_dict, pickRate_dict, tier_dict


def champion_statistics(lane, champion):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = f'https://www.op.gg/champion/{champion}/statistics/{lane}'
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    skillSeq = []
    for i in range(3):
        skill = soup.select(
            'ul.champion-stats__list')[2].find_all('span')[i].text
        skillSeq.append(skill)
    trend_items = []
    if champion == 'Cassiopeia':  # 신발이 없는 챔피언
        item_num = 7
    else:
        item_num = 10
    for i in range(item_num):
        tmp = soup.select(
            'td.champion-overview__data.champion-overview__border.champion-overview__border--first')[i].find_all('img')
        items = ','.join(findItem(tmp))
        items = items.split(',')
        # items = [searchItem(int(key)) for key in keys]
        # items = ', '.join(items)
        pickRate = soup.select(
            '.champion-overview__stats.champion-overview__stats--pick.champion-overview__border')[i].find('strong').text
        pickTotal = soup.select(
            '.champion-overview__stats.champion-overview__stats--pick.champion-overview__border')[i].find('span').text
        winRate = soup.select(
            '.champion-overview__stats.champion-overview__stats--win.champion-overview__border')[i].find('strong').text

        trend_items.append([items, pickRate, pickTotal, winRate])

    data_dict = {
        'img': soup.select_one('.champion-stats-header-info__image').find('img').attrs['src'],
        'tier': soup.select_one('.champion-stats-header-info__tier').find('b').text[-1],
        'win_rank': str(soup.select('.champion-stats-trend-rank')[0].find('b').text + soup.select('.champion-stats-trend-rank')[0].find('span').text).split('/'),
        'win_rate': soup.select('.champion-stats-trend-rate')[0].text.replace('\n\t\t\t', '').replace('\n\t\t', ''),
        'pick_rank': str(soup.select('.champion-stats-trend-rank')[1].find('b').text + soup.select('.champion-stats-trend-rank')[1].find('span').text).split('/'),
        'pick_rate': soup.select('.champion-stats-trend-rate')[1].text.replace('\n\t\t\t', '').replace('\n\t\t', ''),
        'trend_spell1': [findSkill(soup.select('ul.champion-stats__list')[0].find_all('img')[0]),
                         findSkill(soup.select(
                             'ul.champion-stats__list')[0].find_all('img')[1]),
                         soup.select(
                             '.champion-overview__stats.champion-overview__stats--pick')[0].find('strong').text,  # 픽률
                         soup.select('.champion-overview__stats.champion-overview__stats--pick')[
            0].find('span').text,   # 총 표본수
            soup.select('.champion-overview__stats.champion-overview__stats--win')[0].find('strong').text],  # 승률
        'trend_spell2': [findSkill(soup.select('ul.champion-stats__list')[1].find_all('img')[0]),
                         findSkill(soup.select('ul.champion-stats__list')
                                   [1].find_all('img')[1]),
                         soup.select(
                             '.champion-overview__stats.champion-overview__stats--pick')[1].find('strong').text,
                         soup.select(
            '.champion-overview__stats.champion-overview__stats--pick')[1].find('span').text,
            soup.select('.champion-overview__stats.champion-overview__stats--win')[1].find('strong').text],
        'trend_skill': [skillSeq,
                        soup.select(
                            '.champion-overview__stats.champion-overview__stats--pick')[2].find('strong').text,
                        soup.select(
                            '.champion-overview__stats.champion-overview__stats--pick')[2].find('span').text,
                        soup.select('.champion-overview__stats.champion-overview__stats--win')[2].find('strong').text],
        'trend_items': trend_items,
        'counters': [translationChampion2(translation_champion(champ.text.replace('\n', '').replace('\t\t\t\t\t\t\t\t\t', '').replace("'", ''))) for champ in soup.select('.champion-stats-header-matchup__table__champion')],
        'counters_rate': [rate.find('b').text for rate in soup.select('.champion-stats-header-matchup__table__winrate')]
    }

    return data_dict


def counter_matchup(lane, champion):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = f'https://www.op.gg/champion/{champion}/statistics/{lane}/matchup'
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    champ_len = len(soup.select('.champion-matchup-list__champion'))
    enemy_champions = []
    win_rates = []
    totalPlay = []
    totalPlay_rate = []
    for i in range(champ_len):
        champ = soup.select(
            '.champion-matchup-list__champion')[i].find('span').text
        winRate = soup.select(
            '.champion-matchup-list__champion')[i].find_all('span')[1].string
        winRate = [item.strip() for item in winRate if str(item)]
        winRate = ''.join(winRate)
        play_rate = soup.select(
            '.champion-matchup-list__totalplayed')[i].find('span').text
        play_num = soup.select(
            '.champion-matchup-list__totalplayed')[i].find('small').text
        enemy_champions.append(
            (translationChampion2(translation_champion(champ.replace('\n', '').replace('\t\t\t\t\t\t\t\t\t', '').replace("'", '')))))
        win_rates.append(winRate)
        totalPlay.append(play_num)
        totalPlay_rate.append(play_rate)
    data_dict = {
        'enemy_champions': enemy_champions,
        'win_rates': win_rates,
        'totalPlay': totalPlay,
        'totalPlay_rate': totalPlay_rate
    }

    return data_dict
