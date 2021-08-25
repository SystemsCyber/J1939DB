import json
from flask import Flask, jsonify, request, session, make_response
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import jwt
import sqlite3
import uuid
import datetime

app = Flask(__name__)
app.config["Debug"] = True

app.config['SECRET_KEY'] = '38e4623608495761405b08a8e350d2f0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite3:////Users/drumm/PycharmProjects/pythonProject/login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(email=data['email']).first()
        except:
            return jsonify({'message': 'token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorator


# Opens the j1939/logindatabase files and loads them for parsing.
f1 = open("j1939.json")
j1939 = json.load(f1)


# Test function for handling different errors.
@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'Authentication': 'login required'})

    user = Users.query.filter_by(name=auth.username).first()

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'email': user.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)},
                           app.config['SECRET_KEY'], "HS256")
        return jsonify({'token': token})


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)


@app.route('/api/all', methods=['GET'])
# @token_required
def api_all():
    return jsonify(j1939)


@app.route('/api/PGNs/all', methods=['GET'])
# @token_required
def api_pgn_all():
    return jsonify(j1939['J1939PGNdb'])


@app.route('/api/PGNs', methods=['GET'])
# @token_required
def api_pgn():
    if 'pgn' in request.args:
        pgn = request.args['pgn']
    else:
        return "Error: No pgn field provided. Please specify a pgn."
    if pgn in j1939['J1939PGNdb']:
        results = {pgn: j1939['J1939PGNdb'][pgn]}
        return jsonify(results)
    else:
        return make_response({'message': 'PGN does not exist in the database.'})


@app.route('/api/PGNDecoder', methods=['GET'])
# @token_required
def api_pgn_decoder():
    if 'pgn' in request.args:
        pgn = request.args['pgn']
    else:
        return "Error: No pgn field provided. Please specify a pgn."
    SPNs = j1939['J1939PGNdb'][pgn]['SPNs']
    results = []
    for i in SPNs:
        spn = j1939['J1939SPNdb'][str(i)]
        results.append(spn)
    return jsonify(results)


@app.route('/api/SPNs/all', methods=['GET'])
# @token_required
def api_spn_all():
    return jsonify(j1939['J1939SPNdb'])


@app.route('/api/SPNs', methods=['GET'])
# @token_required
def api_spn():
    if 'spn' in request.args:
        spn = request.args['spn']
    else:
        return "Error: No spn field provided. Please specify an spn."
    results = [j1939['J1939SPNdb'][spn]]
    return jsonify(results)
