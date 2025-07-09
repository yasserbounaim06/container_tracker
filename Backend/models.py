from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    container_number = db.Column(db.String(30))
    iso_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
