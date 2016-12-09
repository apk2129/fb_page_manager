#!/usr/bin/env python3


from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,current_user
from oauth import OAuthSignIn
from fbPageManager import FacebookPageManager
from flask.ext.bootstrap import Bootstrap
from flask import request
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required, Length



app = Flask(__name__)

app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '379359885745773',
        'secret': 'dbf43f6584f5f26da3a56028d5711e94'
    }
}

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'
bootstrap = Bootstrap(app)

fb_page_manager = FacebookPageManager()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):

    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, pages = oauth.callback()
    fb_page_manager.initCache(pages)
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/getPages')
def getPages():
    pages = fb_page_manager.get_all_pages_info()
    return render_template('pages.html', pages = pages)


@app.route('/posts/<pageid>/<token>/<page_name>')
def get_page_info( pageid, token, page_name):


    pub_posts,unpub_posts = fb_page_manager.get_posts_per_page(pageid, token)

    print(unpub_posts)
    return render_template('posts.html',token=token, page_name=page_name, pubposts=pub_posts,unpubposts=unpub_posts )

class NameForm(Form):
    description = TextAreaField('description')
    submit = SubmitField('Submit')

@app.route('/postInfo/<postid>/<token>',methods=['GET', 'POST'])
def get_post_info(postid, token):
    post_details = fb_page_manager.get_post_details(postid, token)
    print(post_details['comments'])
    form = NameForm(description=post_details['description'])
    # form.name.data = "test name"
    # if form.validate_on_submit():
    #     name = form.name.data
    #     form.name.data = ''
    return render_template('post_details.html',post_details=post_details, form=form)


@app.route('/publish',methods=['GET','POST'])
def publish_post():

    desc =  request.form['exampleTextarea']
    fb_page_manager.publish_post(desc)

    return redirect(url_for('index'))





if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
