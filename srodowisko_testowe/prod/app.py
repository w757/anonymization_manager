from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.exceptions import BadRequest
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(50))
    nazwisko = db.Column(db.String(50))
    pesel = db.Column(db.String(11))
    email = db.Column(db.String(100))
    telefon = db.Column(db.String(20))
    adres = db.Column(db.String(200))
    stanowisko = db.Column(db.String(100))
    pensja_brutto = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'imie': self.imie,
            'nazwisko': self.nazwisko,
            'pesel': self.pesel,
            'email': self.email,
            'telefon': self.telefon,
            'adres': self.adres,
            'stanowisko': self.stanowisko,
            'pensja_brutto': self.pensja_brutto
        }

#---przesylanie zapytan do proxy----

PROXY_BASE_URL = 'http://127.0.0.1:5001'
SERVICE_UUID = '8ce2e876-723a-4a34-b6cf-77a9a0ea32fa' 

@app.before_request
def log_and_proxy():
    send_to_proxy(request)

def send_to_proxy(request):
    try:
        headers = {
            'Content-Type': request.headers.get('Content-Type', 'application/json'),
            'X-Service-UUID': SERVICE_UUID
        }

        raw_body = request.get_data(as_text=True)
        json_data = raw_body if raw_body.strip() else None
        proxy_url = f"{PROXY_BASE_URL}{request.full_path.rstrip('?')}"

        if request.method in ['POST', 'PUT']:
            requests.request(
                method=request.method,
                url=proxy_url,
                data=json_data,
                headers=headers
            )
    except Exception as e:
        app.logger.error(f"Błąd podczas wysyłania do proxy: {str(e)}")

#---------

@app.route('/')
def employee_list():
    return render_template("employee_list.html")

@app.route('/employee_form')
def employee_form():
    emp_id = request.args.get('id')
    return render_template("employee_form.html", employee_id=emp_id)

@app.route('/api/employees', methods=['GET', 'POST'])
def employees():
    if request.method == 'GET':
        return jsonify([e.to_dict() for e in Employee.query.all()])

    data = request.get_json()
    try:
        emp = Employee(
            imie=data.get('imie'),
            nazwisko=data.get('nazwisko'),
            pesel=data.get('pesel'),
            email=data.get('email'),
            telefon=data.get('telefon'),
            adres=data.get('adres'),
            stanowisko=data.get('stanowisko'),
            pensja_brutto=data.get('pensja_brutto')
        )
        db.session.add(emp)
        db.session.commit()
        return jsonify(emp.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        raise BadRequest(f"Błąd tworzenia: {e}")

@app.route('/api/employees/<int:emp_id>', methods=['GET', 'PUT', 'DELETE'])
def employee_detail(emp_id):
    emp = Employee.query.get_or_404(emp_id)

    if request.method == 'GET':
        return jsonify(emp.to_dict())

    data = request.get_json()
    if request.method == 'PUT':
        try:
            emp.imie = data.get('imie')
            emp.nazwisko = data.get('nazwisko')
            emp.pesel = data.get('pesel')
            emp.email = data.get('email')
            emp.telefon = data.get('telefon')
            emp.adres = data.get('adres')
            emp.stanowisko = data.get('stanowisko')
            emp.pensja_brutto = data.get('pensja_brutto')
            db.session.commit()
            return jsonify(emp.to_dict())
        except Exception as e:
            db.session.rollback()
            raise BadRequest(f"Błąd aktualizacji: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=9010, debug=True)
