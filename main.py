from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
from pprint import pprint

API_KEY = "d6a05580be3a2dcccae6edbb4dc9ab89"
tmdb_endpoint = "https://api.themoviedb.org/3/search/movie"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

all_movies = []
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Float(120), unique=False, nullable=False)
    ranking = db.Column(db.Integer, unique=False, nullable=False)
    review = db.Column(db.String(250), unique=False, nullable=False)
    img_url = db.Column(db.String, unique=False, nullable=False)


    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'

db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()


class EditForm(FlaskForm):
    rating = FloatField('Your rating out of 10 (e.g, 6, 7.5)', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    form = EditForm()
    if request.method == "POST":
        movie_id = request.args.get("id")
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = request.form["rating"]
        movie_to_update.review = request.form["review"]
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_selected, form=form)


@app.route("/home", methods=["GET", "POST"])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()

    if form.validate_on_submit():
        params = {"api_key":  API_KEY,
                  "query": request.form["title"]
        }
        response = requests.get(url=tmdb_endpoint, params=params)
        data = response.json()
        movie_results = data["results"]
        return render_template("select.html", movies=movie_results)

    return render_template("add.html", form=form)


@app.route("/select", methods=["GET", "POST"])
def select():
    return render_template("select.html")


@app.route("/find", methods=["GET", "POST"])
def find():
    movie_id = request.args.get('id')
    print(movie_id)
    tmdb_id_endpoint = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": API_KEY,
              }
    response = requests.get(url=tmdb_id_endpoint, params=params)
    data = response.json()
    pprint(data)
    title = data["title"]
    img_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    year = data["release_date"].split("-")[0]
    description = data["overview"]
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        rating=0,
        ranking=0,
        review="review pending",
        img_url=img_url,
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
