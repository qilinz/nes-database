from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor, CKEditorField
import pandas as pd
from random import choice

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# --------------------------------Create db-------------------------------------------
## CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## CONFIGURE TABLE
class Game(db.Model):
    __tablename__ = "Games"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    developer = db.Column(db.String(250), nullable=False)
    publisher_na = db.Column(db.String(250), nullable=False)
    publisher_eu = db.Column(db.String(250), nullable=False)
    release_na = db.Column(db.String(250), nullable=False)
    release_eu = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250))
    wiki_url = db.Column(db.String(250))
    genre = db.Column(db.String(250))
    multi_support = db.Column(db.String(250), nullable=False)


# db.create_all()

# --------------------------------Add csv to db-------------------------------------------
#
# df = pd.read_csv("game_data_processed.csv")
# game_list = df.to_dict("records")
#
# for game in game_list:
#     new_game = Game(
#         title=game["title"],
#         developer=game["developer"],
#         publisher_na=game["publisher_na"],
#         publisher_eu=game["publisher_eu"],
#         release_na=game["release_na"],
#         release_eu=game["release_eu"],
#         img_url=game["img"],
#         wiki_url=game["wiki_link"],
#         genre=game["genre"],
#         multi_support=game["multi-support"],
#     )
#     db.session.add(new_game)
#     db.session.commit()


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/games')
def games():
    all_games = db.session.query(Game).all()
    return render_template('games.html', games=all_games)


@app.route('/random')
def random():
    all_games = db.session.query(Game).all()
    random_game = choice(all_games)
    return render_template('random.html', game=random_game)



if __name__ == '__main__':
    app.run()
