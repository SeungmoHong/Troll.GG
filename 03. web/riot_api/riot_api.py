from flask import Blueprint, render_template, request, session
from flask import current_app
from util.util import *
import os, json


riot_api = Blueprint('riot_api', __name__)


champion_df, item_df, spell_df, rune_df = new_datas()
menu = {'ho':0, 'ri' :1, 'op' : 0, 'ris' : 1, 'opg' : 0}
version = check_version()

@riot_api.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        nickname = request.form['nickname']
        userId, userAccountId, userPuuid, userNickname, userLevel, profileIconId = searchUserId(nickname)
        tier, rank, wins, losses = userInfo(userId)
        tier = tier.lower().capitalize()
        winning_rate = round(wins / (wins + losses) * 100, 2)

        data_url = f'http://ddragon.leagueoflegends.com/cdn/{version}'
        profileIcon = data_url + f'/img/profileicon/{profileIconId}.png'
        champion_url = '/img/champion/'
        item_url = '/img/item/'
        spell_url = '/img/spell/'
        
        url_list = [data_url, champion_url, item_url, spell_url]
        
        tier_img = f"/static/img/Emblem_{tier}.png"
        img_url = f"/static/img/" 
        result = [userNickname, userLevel, tier, rank, wins, losses, winning_rate, profileIcon]
        matches_info = userMatches_record(userNickname)

        kor_champions = [translationChampion(champ) for champ in matches_info['champion']]
        kor_all_champions = []
        for i in range(len(matches_info['all_champions'])):
            kor_all_champion = [translationChampion(champ) for champ in matches_info['all_champions'][i]]
            kor_all_champions.append(kor_all_champion)
        main_runes = {'8000.png' : '정밀', '8100.png' : '지배', '8200.png' : '마법', '8300.png' : '영감', '8400.png' : '결의'}
        kor_main_spells = []
        for i i in range(len(matches_info['spell'])):
            kor_main_spell = [translationSpell(eng) for eng in matches_info['spell'][i]]
            kor_main_spells.append(kor_main_spell)

        if matches_info['result'].count('승') == 0:
            winning_rate = 0
        else:
            winning_rate = round(matches_info['result'].count('승') / len(matches_info['result']) * 100,2)

        if matches_info['trolling'].count(True) == 0:
            trolling = 0
        else:
            trolling = round(matches_info['trolling'].count(True) / len(matches_info['trolling']) * 100,2)

        win_consecutive = 0
        for recentData in matches_info['result']:
            if matches_info['result'][0] == recentData:
                win_consecutive += 1
            else:
                break

        recentHistory = [matches_info['result'].count('승'), matches_info['result'].count('패'), winning_rate, win_consecutive, trolling]

        
        return render_template('riot_api/search.html', menu=menu, version= version, 
        result = result, tier_img=tier_img, matches_info=matches_info, url_list = url_list, img_url = img_url, recentHistory=recentHistory,
        kor_champions= kor_champions, kor_all_champions=kor_all_champions, main_runes=main_runes, kor_main_spells=kor_main_spells)

