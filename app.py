"""Docstring Recipe Tracker
A recipe tracker for Stardew Valley.
Users can easily add the recipes they have completed to a list to keep track.
By Miguel Monreal on 12/02/26"""

from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (UserMixin, login_user, LoginManager,
                         login_required, logout_user, current_user)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from config import ZERO
import os


# Initialize App
app = Flask(__name__)

# Initialize the DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "recipes.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "secret_shhhh"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


recipe_ingredient = db.Table(
    "recipe_ingredient",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id")),
    db.Column("ingredient_id", db.Integer, db.ForeignKey("ingredient.id"))
)

recipe_account = db.Table(
    "recipe_account",
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipe.id")),
    db.Column("account_id", db.Integer, db.ForeignKey("account.id")),
    db.Column("status", db.Integer)
)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    ingredients = db.relationship("Ingredient", secondary=recipe_ingredient,
                                  backref="recipes", lazy=True)
    
    accounts = db.relationship("Account", secondary=recipe_account,
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

    password = PasswordField(validators=[
        InputRequired(),
        Length(min=4, max=20),
        EqualTo("confirm_password", message="Passwords must match")],
        render_kw={"placeholder": "Password"}
    )

    confirm_password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Confirm Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_account_username = Account.query.filter_by(
            username=username.data).first()

        if existing_account_username:
            raise ValidationError(
                "That username already exists. Please choose a different one."
            )


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Home Page
@app.route("/")
def home():
    recipes = Recipe.query.all()

    return render_template("index.html", recipes=recipes, header="Home")


# Individual recipe page displaying necessary ingredients
@app.route("/recipe/<int:id>", methods=["GET", "POST"])
def recipe(id):
    recipe = Recipe.query.get_or_404(id)

    if request.method == "POST":
        add_recipe(id)

    return render_template("recipe.html", recipe=recipe)


def add_recipe(id):
    Recipe.query.filter_by(id=id, status=ZERO)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Account.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("home"))

    return render_template("login.html", header="Login", form=form)


# Registers new accounts, adding to database
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    # On validation generate hashed password and add account
    if (form.validate_on_submit()):
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Account(username=form.username.data,
                           password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("home"))

    return render_template("register.html", header="Register", form=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
