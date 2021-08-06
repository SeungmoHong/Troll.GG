from flask import Blueprint, render_template, request, session
from flask import current_app
from util.util import *


opgg_crawling = Blueprint('opgg', __name__)


champion_df, item_df, spell_df, rune_df = new_datas()
menu = {'ho':0, 'ri' :0, 'op' : 1, 'ris' : 0, 'opg' : 1}
version = check_version()



@opgg_crawling.route('/statistics', methods=['GET', 'POST'])
def statistics(): 
    img_link = 'http://ddragon.leagueoflegends.com/cdn/' + str(version) + '/img/champion/'
    lanes = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
    champion_dict, winRate_dict, pickRate_dict, tier_dict = tier_list()
    top_count = len(champion_dict['TOP'])
    jg_count = len(champion_dict['JUNGLE'])
    mid_count = len(champion_dict['MID'])
    adc_count = len(champion_dict['ADC'])
    sup_count = len(champion_dict['SUPPORT'])
    eng_champion_dict = {}
    for lane in lanes:
        eng_champion_dict[lane] = [translationChampion2(champion) for champion in champion_dict[lane]]
    return render_template('opgg/statistics.html', menu=menu, version= version,
    img_link=img_link, champion_dict=champion_dict, winRate_dict=winRate_dict, pickRate_dict=pickRate_dict,
    tier_dict=tier_dict, eng_champion_dict=eng_champion_dict, top_count=top_count, jg_count=jg_count, mid_count=mid_count,
    adc_count=adc_count, sup_count=sup_count)

@opgg_crawling.route('/statistics/<lane>/<champion>')
def championStatistics(lane,champion):
    lane = lane
    champion = champion
    url = f'https://www.op.gg/champion/{champion}/statistics/{lane}'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    win_rank = soup.select('.champion-stats-trend-rank')[0].find('b').text + soup.select('.champion-stats-trend-rank')[0].find('span').text
    pick_rank = soup.select('.champion-stats-trend-rank')[1].find('b').text + soup.select('.champion-stats-trend-rank')[1].find('span').text
    pass
