from __main__ import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class Producto(db.Model):
    NumProducto = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(50), nullable=False)
    PrecioUnitario = db.Column(db.Float, nullable=False)
    Item=db.relationship('Item',backref='producto',cascade='all, delete-orphan',lazy='dynamic')

class Item(db.Model):
    NumItem = db.Column(db.Integer, primary_key=True)
    NumPedido = db.Column(db.Integer,db.ForeignKey('pedido.NumPedido'))
    NumProducto = db.Column(db.Integer,db.ForeignKey('producto.NumProducto'))
    Precio = db.Column(db.Float, nullable=False)
    Estado = db.Column(db.String(30), nullable=False)

class Pedido(db.Model):
    NumPedido = db.Column(db.Integer, primary_key=True)
    Fecha = db.Column(db.DateTime)
    Total = db.Column(db.Float, nullable=False)
    Cobrado = db.Column(db.Boolean, nullable=False)
    Observacion = db.Column(db.Text)
    DNIMozo = db.Column(db.String(10), nullable=False)
    Mesa = db.Column(db.Integer, nullable=False)
    Item=db.relationship('Item',backref='pedido',cascade='all, delete-orphan',lazy='dynamic')

class Usuario(db.Model):
    DNI = db.Column(db.Integer, primary_key=True)
    Clave = db.Column(db.String(50), nullable=False)
    Tipo = db.Column(db.String(50), nullable=False)
