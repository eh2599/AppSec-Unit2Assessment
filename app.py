import secrets
import subprocess

from flask import Flask, render_template, request, session, make_response
from flask_bcrypt import Bcrypt

app = Flask(__name__)
secret_key = secrets.token_urlsafe(32)
app.config['SECRET_KEY'] = secret_key
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=600
)

bcrypt = Bcrypt(app)

registered_users = {}


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        response = make_response(render_template('logged_in_index.html', username=username))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    else:
        response = make_response(render_template('index.html'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


def register_with_user_info(username, hashed_password, phone):
    if username in registered_users:
        response = make_response(render_template('username_already_exists.html', username=username))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    else:
        registered_users[username] = [hashed_password, phone]
        response = make_response(render_template('registration_complete.html', username=username))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        response = make_response(render_template('register.html'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    elif request.method == 'POST':
        username = request.values['uname']
        hashed_password = bcrypt.generate_password_hash(request.values['pword']).decode('utf-8')
        phone = request.values['2fa']
        response = make_response(register_with_user_info(username, hashed_password, phone))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


def check_user_authentication(username, password, phone):
    if username not in registered_users:
        response = make_response(render_template('login_failure.html'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    else:
        if bcrypt.check_password_hash(registered_users[username][0], password):
            if phone == registered_users[username][1]:
                session.clear()
                session['username'] = username
                session.permanent = True
                response = make_response(render_template('login_success.html'))
                response.headers['Content-Security-Policy'] = "default-src 'self'"
                return response
            else:
                response = make_response(render_template('tfa_failure.html'))
                response.headers['Content-Security-Policy'] = "default-src 'self'"
                return response
        else:
            response = make_response(render_template('login_failure.html'))
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            return response


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        response = make_response(render_template('login.html'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    elif request.method == 'POST':
        username = request.values['uname']
        password = request.values['pword']
        phone = request.values['2fa']
        response = make_response(check_user_authentication(username, password, phone))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


@app.route('/spell_check', methods=['POST', 'GET'])
def spell_check():
    if 'username' in session:
        username = session['username']
        if request.method == 'GET':
            response = make_response(render_template('spell_check.html', username=username))
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            return response
        elif request.method == 'POST':
            fp = open('input_text.txt', 'w')
            fp.write(str(request.values['inputtext']))
            fp.close()
            text_to_check = str(request.values['inputtext'])
            result = subprocess.check_output(["./a.out", "input_text.txt", "wordlist.txt"]).decode(
                "utf-8").strip().replace('\n', ', ')
            response = make_response(render_template('spell_check_results.html', text_to_check=text_to_check, result=result))
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            return response
    else:
        response = make_response(render_template('not_logged_in.html'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response


@app.route('/logout')
def logout():
    session.pop('username', None)
    response = make_response(render_template('index.html'))
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    app.run()
