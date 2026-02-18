"""Docstring Recipe Tracker
A recipe tracker for Stardew Valley.
Users can easily add the recipes they have completed to a list to keep track.
By Miguel Monreal on 12/02/26"""

from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (login_user, LoginManager,
                         login_required, logout_user, current_user)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from config import ZERO, STATUS_CHOICES
from models import (Account, Recipe, RecipeAccount,
                    Ingredient)
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
@app.route("/recipe/<int:id>")
def recipe(id):
    recipe = Recipe.query.get_or_404(id)

    status = ZERO
    if current_user.is_authenticated:
        link = RecipeAccount.query.filter_by(
            recipe_id=id,
            account_id=current_user.id
        ).first()

        status = link.status if link else ZERO

    return render_template("recipe.html", recipe=recipe,
                           status_choices=STATUS_CHOICES,
                           status=status)

@app.route("/update-recipe-status", methods=["GET", "POST"])
@login_required
def update_recipe_status():
    data = request.get_json()

    # Gets the recipe linked with account (to use the status)
    link = RecipeAccount.query.filter_by(
        recipe_id=data["id"],
        account_id=current_user.id
    ).first()

    # Ensures status is valid
    if data["status"] in [0, 1, 2]:
        # Adds or updates row depending on if it exists
        if not link:
            link = RecipeAccount(
                recipe_id=data["id"],
                account_id=current_user.id,
                status=data["status"]
            )
            db.session.add(link)
        else:
            link.status = data["status"]

        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False}), 404


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
