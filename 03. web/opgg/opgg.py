from flask import Blueprint, render_template, request, session
from flask import current_app
from util.util import *

opgg_crawling = Blueprint('opgg', __name__)


champion_df, item_df, spell_df, rune_df = new_datas()
menu = {'ho':0, 'ri' :0, 'op' : 1, 'ris' : 0, 'opg' : 1}
version = check_version()



@opgg_crawling.route('/statistics', methods=['GET', 'POST'])
def statistics():
    return render_template('opgg/statistics.html', menu=menu, version= version)