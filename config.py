from flask_sqlalchemy import SQLAlchemy

# Constants
ZERO = 0
OWNED = 1
COOKED = 2

STATUS_CHOICES = {
    0: "Not Owned",
    1: "Owned",
    2: "Cooked"
}

db = SQLAlchemy()
