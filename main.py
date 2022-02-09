import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
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

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


## API setup
TopSecretKey = os.environ.get("API_KEY")


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


@app.route('/api')
def api():
    host_url = os.environ.get("HOST_URL")
    return render_template("api.html", url=host_url)


# --------------------------------API response------------------------------------------
@app.route('/api/random')
def api_random():
    all_games = db.session.query(Game).all()
    random_game = choice(all_games)
    return jsonify(game=random_game.to_dict())


@app.route('/api/all')
def api_all():
    all_games = db.session.query(Game).all()
    game_list = [game.to_dict() for game in all_games]
    return jsonify(games=game_list)


@app.route('/api/search')
def api_search():
    title = request.args.get("title")
    game = Game.query.filter_by(title=title).first()
    if not game:
        return jsonify(
            error={
                "Not Found": "Sorry, this game is not on NES."
            }
        ), 404
    return jsonify(games=game.to_dict())


@app.route('/api/update-genre/<int:game_id>', methods=["PATCH"])
def api_update_genre(game_id):
    game_to_update = Game.query.get(game_id)
    if not game_to_update:
        return jsonify(
            error={
                "Not Found": "Sorry, we don't have a game with the given id."
            }
        ), 404
    game_to_update.genre = request.args.get("new_genre")
    db.session.commit()
    return jsonify(
        message={
            "Success": "Update the game genre successfully."
        }
    ), 200


@app.route('/api/add', methods=["POST"])
def api_add():
    game_title = request.form.get("title")
    if Game.query.filter_by(title=game_title).first():
        return jsonify(
            error={
                "Bad Request": "This game already exists. "
            }
        ), 400
    new_game = Game(
        title=request.form.get("title"),
        developer=request.form.get("developer"),
        publisher_na=request.form.get("publisher_na"),
        publisher_eu=request.form.get("publisher_eu"),
        release_na=request.form.get("release_na"),
        release_eu=request.form.get("release_eu"),
        img_url=request.form.get("img_link"),
        wiki_url=request.form.get("wiki_link"),
        genre=request.form.get("genre"),
        multi_support=bool(request.form.get("multi_support")),
    )
    db.session.add(new_game)
    db.session.commit()
    return jsonify(
        message={
            "Success": "Add the game successfully."
        }
    ), 200


@app.route('/api/delete/<int:game_id>', methods=["DELETE"])
def api_delete(game_id):
    user_key = request.args.get("api_key")
    if user_key != TopSecretKey:
        return jsonify(
            error={
                "Not Allowed": "Sorry, that's not allowed. Make sure you have the correct api_key."
            }
        ), 403
    game_to_delete = Game.query.get(game_id)
    if game_to_delete:
        db.session.delete(game_to_delete)
        db.session.commit()
        return jsonify(
            message={
                "Success": "Delete the game successfully."
            }
        ), 200
    return jsonify(
        error={
            "Not Found": "Sorry, we don't have a game with the given id."
        }
    ), 404


if __name__ == '__main__':
    app.run()
