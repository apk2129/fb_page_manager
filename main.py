from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
import facebook

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    pages  = get_facebook_pages() #return page Id
    print(pages)
    return render_template('index.html', city='Pages', pages = pages)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')

user_token   = 'EAACEdEose0cBAPCFPUKQpDgzIYHrlZBpxqqpdzf9bmFIZAwoAoZAl6gYyk8OqevklxpaTlK7A6LbqKJInMFjZAkwpyxWzBHZCxMIkfyWfvqnE8WautqZB43tMWP7QJef8JY67MSQSForZCSQNo2BdulX4EHJ1mAxhL4UgAigB4AvAZDZD'

def get_facebook_pages():

    graph   = facebook.GraphAPI(access_token=user_token)
    pages   = graph.get_connections("me", "accounts")['data']

    p = {}
    for page in pages:
        p[page['id']] = page['name']

    return p

@app.route('/postInfo/<pid>')
def get_page_info(pid):

    # pid = '469888179740276'
    graph = facebook.GraphAPI(user_token)
    profile = graph.get_object(pid)
    posts = graph.get_connections(pid, 'posts')
    p = [ post['id'] for post in posts['data']]
    return render_template('postInfo.html',posts=p)

if __name__ == '__main__':
    app.run(debug=True)
