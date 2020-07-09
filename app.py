from flask import Flask, render_template, request, session
import subprocess, secrets

app = Flask(__name__)
secret_key = secrets.token_urlsafe(32)
app.config['SECRET_KEY'] = secret_key

registered_users = {}


@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Home Page</title>
        </head>
        <body>
            <h3>You are logged in.<h3>
            <h1>Welcome to the Spell Checker Tool!</h1>
            <p><a href="/spell_check">Spell Checker</a></p>
            <p><a href="/register">Register a new user</a></p>
            <p><a href="/logout">Logout</a></p>
        </body>
        </html>
        '''
    else:
        return render_template('index.html')


def register_with_user_info(username, password, phone):
    if username in registered_users:
        return render_template('username_already_exists.html', username=username)
    else:
        registered_users[username] = [password, phone]
        return render_template('registration_complete.html', username=username)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.values['uname']
        password = request.values['pword']
        phone = request.values['2fa']
        return register_with_user_info(username, password, phone)


def check_user_authentication(username, password, phone):
    if username not in registered_users:
        return render_template('login_failure.html')
    else:
        if password == registered_users[username][0]:
            if phone == registered_users[username][1]:
                session['username'] = username
                return render_template('login_success.html')
            else:
                return render_template('tfa_failure.html')
        else:
            return render_template('login_failure.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.values['uname']
        password = request.values['pword']
        phone = request.values['2fa']
        return check_user_authentication(username, password, phone)


@app.route('/spell_check', methods=['POST', 'GET'])
def spell_check():
    if 'username' in session:
        username = session['username']
        if request.method == 'GET':
            return render_template('spell_check.html', username=username)
        elif request.method == 'POST':
            fp = open('input_text.txt', 'w')
            fp.write(str(request.values['inputtext']))
            fp.close()
            text_to_check = str(request.values['inputtext'])
            result = subprocess.check_output(["./a.out", "input_text.txt", "wordlist.txt"]).decode(
                "utf-8").strip().replace('\n', ', ')
            return render_template('spell_check_results.html', text_to_check=text_to_check, result=result)
    else:
        return '''
        <html>
        <head>
            <title>Not Logged In</title>
        </head>
        <body>
            <h1>You are not logged in.<h1>
            <h3>Please register as a new user or login to use the spell checker tool.</h3>
            <p><a href="/login">Login</a></p>
            <p><a href="/register">Register</a></p>
        </body>
        </html> '''


@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
