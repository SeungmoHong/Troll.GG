from flask import Flask, render_template, session
import os, json
import pandas as pd


app = Flask(__name__)
app.secret_key = 'qwert12345'
app.config['SESSION_COOKIE_PATH'] = '/'


@app.route('/')
def index():
    menu = {'ho':1, 'da':0, 'ml':0, 'se':0, 'co':0, 'cg':0, 'cr':0, 'wc':0,
            'cf':0, 'ac':0, 'rg':0, 'cl':0}
    return render_template('main.html', menu=menu)

if __name__ == '__main__':
    app.run(debug=True)