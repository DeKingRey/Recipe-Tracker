from app import db
from flask_login import UserMixin


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

    recipe_links = db.relationship("RecipeAccount", back_populates="recipe")

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

    account_links = db.relationship("RecipeAccount", back_populates="account")


class RecipeAccount(db.Model):
    recipe_id = db.Column(db.Integer,
                          db.ForeignKey("recipe.id"), primary_key=True)
    account_id = db.Column(db.Integer,
                           db.ForeignKey("account.id"), primary_key=True)
    status = db.Column(db.Integer)

    recipe = db.relationship("Recipe", back_populates="recipe_links")
    account = db.relationship("Account", back_populates="account_links")
