from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
import facebook
import requests

app = Flask(__name__)


@app.route('/')
def index():
    get_long_lived_access_token()
    return render_template('index.html')#, city='Pages', pages = pages)



def get_long_lived_access_token():

    APP_ID       = '379359885745773'
    REDIRECT_URL = 'http://127.0.0.1:5000/'
    #1 The OAuth Dialog
    URL = "https://www.facebook.com/dialog/oauth?client_id=<"+APP_ID+" >\
          &redirect_uri=<"+REDIRECT_URL+">\
          &scope=manage_pages%2Cpublish_stream\
          &state=<STATE>"


# https://www.facebook.com/dialog/oauth?client_id=<588675761327475>&redirect_uri=<http://127.0.0.1:5000/>&scope=manage_pages%2Cpublish_stream&state=<STATE>
    session = requests.Session()

    response = session.request("GET", URL )
    print("***********************************")
    print(URL)
    print(response)
    print("***********************************")


if __name__ == '__main__':
    app.run(debug=True)
