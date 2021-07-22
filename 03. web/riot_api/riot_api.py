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
        

        
        return render_template('riot_api/search.html', menu=menu, result = result, tier_img=tier_img, matches_info=matches_info, url_list = url_list, img_url = img_url)
