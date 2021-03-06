from flask import Flask, render_template, session
from riot_api.riot_api import riot_api
from opgg.opgg import opgg_crawling
import os
import json
import pandas as pd
from util.util import *


app = Flask(__name__)
app.secret_key = 'qwert12345'
app.config['SESSION_COOKIE_PATH'] = '/'


app.register_blueprint(riot_api, url_prefix='/riotapi')
app.register_blueprint(opgg_crawling, url_prefix='/opgg')


@app.route('/')
def index():
    menu = {'ho': 1}

    return render_template('main.html', menu=menu, version=check_version())


if __name__ == '__main__':
    app.run(debug=True)
