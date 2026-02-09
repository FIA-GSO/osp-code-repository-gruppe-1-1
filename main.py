from flask import Flask, request, session, redirect, url_for, render_template, jsonify, redirect, flash
from database.model.base import db
from services.accountService import create_account as service_create_account, login_user as service_login_user

app = Flask(__name__)
app.secret_key = b'dlajwasdhdddqwf98fg9f23803f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/", methods=['GET'])
def index():
    if session.get('account', None) is not None:
        return render_template('index.html')
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')

@app.route("/login_user", methods=['POST'])
def login_user():
    service_login_user()
    return redirect(url_for('index'))

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('account', None)
    flash('Erfolgreich ausgeloggt!', "success")
    return redirect(url_for('index'))

@app.route("/register_account", methods=['GET'])
def register_account():
    return render_template('register.html')

@app.route("/create_account", methods=['POST'])
def create_account():
    service_create_account()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=4000, debug=True)


