"""Docstring Recipe Tracker
A recipe tracker for Stardew Valley, users can easily add the recipes they have completed to a list to keep track.
By Miguel Monreal on 12/02/26"""

from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import wtforms
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import os


# Initialize App
app = Flask(__name__)

# Initialize the DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "recipes.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "secret_shhhh"
db = SQLAlchemy(app)

recipe_ingredient = db.Table(
    "recipe_ingredient",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id")),
    db.Column("ingredient_id", db.Integer, db.ForeignKey("ingredient.id"))
)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    ingredients = db.relationship("Ingredient", secondary=recipe_ingredient,
                                  backref="recipes", lazy=True)

    def __repr__(self):
        return f"Recipe {self.name}"


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"Ingredient {self.name}"


class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_account_username = Account.query.filter_by(
            username=username.data).first()

        if existing_account_username:
            raise ValidationError(
                "That username already exists. Please choose a different one."
            )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Home Page
@app.route("/")
def home():
    recipes = Recipe.query.all()

    return render_template("index.html", recipes=recipes, header="Home")


# Individual recipe page displaying necessary ingredients
@app.route("/recipe/<int:id>")
def recipe(id):
    recipe = Recipe.query.get_or_404(id)

    return render_template("recipe.html", recipe=recipe)


@app.route("/login")
def login():
    return render_template("login.html", header="Login")


@app.route("/register")
def register():
    return render_template("register.html", header="Register")


if __name__ == "__main__":
    app.run(debug=True)
