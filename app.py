from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

registered_users = {}


@app.route('/')
def index():
    return render_template('base.html')


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
    if request.method == 'GET':
        return render_template('spell_check.html')
    elif request.method == 'POST':
        fp = open('input_text.txt', 'w')
        fp.write(str(request.values['inputtext']))
        fp.close()
        text_to_check = str(request.values['inputtext'])
        result = subprocess.check_output(["./a.out", "input_text.txt", "wordlist.txt"]).decode("utf-8").strip().replace('\n', ', ')
        return render_template('spell_check_results.html', text_to_check=text_to_check, result=result)


if __name__ == '__main__':
    app.run()
