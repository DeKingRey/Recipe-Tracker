"""Docstring Recipe Tracker
A recipe tracker for Stardew Valley, users can easily add the recipes they have completed to a list to keep track.
By Miguel Monreal on 12/02/26"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, select
import sqlite3

DATABASE = "recipes.db"

# Initialize App
app = Flask(__name__)

# Initialize the DB
app.config["SQLALCHEMY_DATABASE_URI"] = "recipes.db"
db = SQLAlchemy(app)


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))


@app.route("/")
def home():
    # Home Page

    items = db.session.execute(select(Recipe)).scalars()

    return render_template("index.html", items)


@app.route("/recipe/<int:id>")
def recipe(id):
    # Returns ingredients needed for corresponding recipe
    sql = """SELECT Recipe.name as recipe_name,
            GROUP_CONCAT(Ingredient.name, ', ') AS ingredients
            FROM Recipe
            JOIN Recipe_Ingredient
                ON Recipe_Ingredient.recipe_id = Recipe.id
            JOIN Ingredient
                ON Ingredient.id = Recipe_Ingredient.ingredient_id
            WHERE Recipe.id = ?
            GROUP BY Recipe.id, Recipe.name;"""
    return str(sql)


if __name__ == "__main__":
    app.run(debug=True)
