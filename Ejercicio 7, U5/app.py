from flask import Flask, render_template, redirect, url_for, g, request, session
import hashlib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile("config.py")
from models import db
from models import Producto, Item, Pedido, Usuario


@app.route('/')
def index():
    return render_template('Bienvenida.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if not ('DNI' in session):
        if request.method == 'POST':
            if not request.form['DNI'] or not request.form['Contraseña']:
                return render_template('Login.html', error="Por favor complete los campos.")
            else:
                error = None
                try:
                    dni = int(request.form['DNI'])
                    usuario_actual = Usuario.query.filter_by(DNI=dni).first()
                    if usuario_actual is None:
                        error = 'DNI o Contraseña incorrecta.'
                    if error == None:
                        clave = hashlib.md5(bytes(request.form["Contraseña"], encoding='utf-8'))
                        if usuario_actual.Clave == clave.hexdigest():
                            session['DNI'] = usuario_actual.DNI
                            funcion = None
                            if usuario_actual.Tipo == "Mozo":
                                funcion = 'Menu_Mozo'
                            else:
                                funcion = 'Marcar_items'
                            return redirect(url_for(funcion))
                        else:
                            error = 'DNI o Contraseña incorrecta.'
                except:
                    error = 'DNI o Contraseña incorrecta.'
                finally:
                    if error != None:
                        return render_template('Login.html', error=error)
        else:
            return render_template('Login.html')
    else:
        usuario_actual = Usuario.query.filter_by(DNI=session.get('DNI')).first()
        if usuario_actual.Tipo == "Mozo":
            funcion = 'Menu_Mozo'
        else:
            funcion = 'Marcar_items'
        return redirect(url_for(funcion))


@app.route('/Menu_Mozo', methods=['POST', 'GET'])
def Menu_Mozo():
    if 'DNI' in session:
        usuario_actual = Usuario.query.filter_by(DNI=session.get('DNI')).first()
        if usuario_actual.Tipo == "Cocinero":
            return redirect(url_for('Marcar_items'))
        return render_template('Menu_mozo.html')
    else:
        return render_template('Error.html', error='No se inicio sesión.')


@app.route('/Registrar_Pedido', methods=['POST', 'GET'])
def Registrar_pedido():
    if 'DNI' in session:
        usuario_actual = Usuario.query.filter_by(DNI=session.get('DNI')).first()
        if usuario_actual.Tipo == "Cocinero":
            return redirect(url_for('Marcar_items'))
        if request.method == 'POST':
            valores = list(dict(request.form).keys())
            pedido = None
            if 'NumPedido' in valores:
                pedido = Pedido.query.filter_by(NumPedido=request.form['NumPedido']).first()
            if 'Mesa' in valores:
                try:
                    numeromesa = int(request.form['Mesa'])
                except:
                    return render_template('Numero_mesa.html', error='Solo se aceptan números.')
                else:
                    pedido = Pedido(Fecha=datetime.now(), Total=0.0, Cobrado=False, Observacion='',
                                    DNIMozo=session.get('DNI'), Mesa=numeromesa)
                    db.session.add(pedido)
                    db.session.commit()
                    return render_template('Registrar_pedido.html', carta=Producto.query.all(), items=None,
                                           Pedido=pedido)
            elif 'Finalizar' in valores:
                return render_template('Observaciones.html', Pedido=pedido)
            elif 'FinalizarPedido' in valores:
                pedido.Observacion = request.form['Observaciones']
                db.session.add(pedido)
                db.session.commit()
                return redirect(url_for('Menu_Mozo'))
            else:
                numprod = valores[1]
                prod = Producto.query.filter_by(NumProducto=numprod).first()
                item = Item(NumPedido=pedido.NumPedido, NumProducto=prod.NumProducto, Precio=prod.PrecioUnitario,
                            Estado='Pendiente')
                db.session.add(item)
                db.session.commit()
            return render_template('Registrar_pedido.html', carta=Producto.query.all(), Pedido=pedido)
        return render_template('Numero_mesa.html')
    return render_template('Error.html', error='No se inicio sesión.')


@app.route('/Visualizar_Pedidos', methods=['POST', 'GET'])
def Visualizar_pedidos():
    if 'DNI' in session:
        usuario_actual = Usuario.query.filter_by(DNI=session.get('DNI')).first()
        if usuario_actual.Tipo == "Cocinero":
            return redirect(url_for('Marcar_items'))
        return render_template('Visualizar_pedidos.html', pedidos=Pedido.query.all(), prod=Producto.query.all())
    else:
        return render_template('Error.html', error='No se inicio sesión')


def listaPedidos():
    pedidos = Pedido.query.all()
    lista = []
    for j in pedidos:
        i = 0
        band = False
        items = Item.query.filter_by(NumPedido=j.NumPedido).all()
        long = len(items)
        while i < long and not band:
            if items[i].Estado == "Pendiente":
                band = True
                lista.append(j)
            i += 1
    return lista


@app.route("/Marcar_Items", methods=["GET", "POST"])
def Marcar_items():
    if 'DNI' in session:
        usuario_actual = Usuario.query.filter_by(DNI=session.get('DNI')).first()
        if usuario_actual.Tipo == "Mozo":
            return redirect(url_for('Menu_Mozo'))
        if request.method == "POST":
            it = Item.query.filter_by(NumItem=request.form["item"]).first()
            it.Estado = "Listo"
            db.session.add(it)
            db.session.commit()
        listaP = listaPedidos()
        return render_template("Marcar_items.html", pedidos=listaP, prod=Producto.query.all(), band=False)
    else:
        return render_template("Error.html", error="No se inicio sesión")


@app.route('/Registrar_Cobro', methods=['POST', 'GET'])
def Registrar_Cobro():
    if 'DNI' in session:
        usuario_actual = Usuario.query.filter_by(DNI=session.get('DNI')).first()
        if usuario_actual.Tipo == "Cocinero":
            return redirect(url_for('Marcar_items'))
        idpedido = None
        if request.method == 'POST':
            valores = list(dict(request.form).keys())
            if 'ID_Pedido' in valores:
                idpedido = request.form['ID_Pedido']
            elif 'Aceptar' in valores:
                pedido = Pedido.query.filter_by(NumPedido=request.form['ID']).first()
                total = 0
                i = 0
                lista = list(pedido.Item)
                bandera = True
                while i < len(lista) and bandera:
                    total += lista[i].Precio
                    if lista[i].Estado != 'Listo':
                        bandera = False
                    i += 1
                if not (bandera):
                    total = False
                return render_template('Confirmar_cobro.html', Total=total, ID_Pedido=request.form['ID'])
            elif 'Confirmar' in valores:
                total = float(request.form['Total'])
                pedido = Pedido.query.filter_by(NumPedido=request.form['ID']).first()
                pedido.Total = total
                pedido.Cobrado = True
                db.session.add(pedido)
                db.session.commit()
        return render_template('Registrar_Cobro.html', pedidos=Pedido.query.all(), prod=Producto.query.all(),
                               IDPedido=idpedido)
    else:
        return render_template("Error.html", error="No se inicio sesión.")


@app.route('/Cerrar_Sesion')
def Cerrar_sesion():
    if 'DNI' in session:
        session.pop('DNI', None)
        return redirect(url_for('index'))
    else:
        return render_template("Error.html", error="No se inicio sesión.")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
