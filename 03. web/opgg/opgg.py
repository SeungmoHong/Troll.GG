from flask import Blueprint, render_template, request, session
from flask import current_app
from util.util import *


opgg_crawling = Blueprint('opgg', __name__)


champion_df, item_df, spell_df, rune_df = new_datas()
menu = {'ho': 0, 'ri': 0, 'op': 1, 'ris': 0, 'opg': 1}
version = check_version()


@opgg_crawling.route('/statistics', methods=['GET', 'POST'])
def statistics():
    img_link = 'http://ddragon.leagueoflegends.com/cdn/' + \
        str(version) + '/img/champion/'
    lanes = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
    champion_dict, winRate_dict, pickRate_dict, tier_dict = tier_list()
    top_count = len(champion_dict['TOP'])
    jg_count = len(champion_dict['JUNGLE'])
    mid_count = len(champion_dict['MID'])
    adc_count = len(champion_dict['ADC'])
    sup_count = len(champion_dict['SUPPORT'])
    eng_champion_dict = {}
    for lane in lanes:
        eng_champion_dict[lane] = [translationChampion2(
            champion) for champion in champion_dict[lane]]
    return render_template('opgg/statistics.html', menu=menu, version=version,
                           img_link=img_link, champion_dict=champion_dict, winRate_dict=winRate_dict, pickRate_dict=pickRate_dict,
                           tier_dict=tier_dict, eng_champion_dict=eng_champion_dict, top_count=top_count, jg_count=jg_count, mid_count=mid_count,
                           adc_count=adc_count, sup_count=sup_count)


@opgg_crawling.route('/statistics/<lane>/<champion>')
def championStatistics(lane, champion):
    lane = lane
    champion = champion
    data_dict = champion_statistics(lane, champion)
    kor_lane_dict = {'top': '탑', 'jungle': '정글',
                     'mid': '미드', 'adc': '원딜', 'support': '서포터'}
    kor_lane = kor_lane_dict[lane]
    kor_champion = translation_champion(champion)

    if champion == 'Cassiopeia':
        return render_template('opgg/champion_statistics(cassiopeia).html', menu=menu, version=version,
                               kor_lane=kor_lane, kor_champion=kor_champion, data_dict=data_dict, champion=champion, lane=lane)
    else:
        return render_template('opgg/champion_statistics.html', menu=menu, version=version,
                               kor_lane=kor_lane, kor_champion=kor_champion, data_dict=data_dict, champion=champion, lane=lane)


@opgg_crawling.route('/counter_matchup/<lane>/<champion>')
def counterMatchup(lane, champion):
    lane = lane
    champion = champion
    kor_lane_dict = {'top': '탑', 'jungle': '정글',
                     'mid': '미드', 'adc': '원딜', 'support': '서포터'}
    kor_lane = kor_lane_dict[lane]
    kor_champion = translation_champion(champion)
    counter_dict = counter_matchup(lane, champion)
    couter_count = len(counter_dict['enemy_champions'])

    return render_template('opgg/counter_matchup.html', menu=menu, version=version,  kor_champion=kor_champion, kor_lane=kor_lane, counter_dict=counter_dict, couter_count=couter_count)
