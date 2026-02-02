from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from database.model.base import db

app = Flask(__name__)
app.secret_key = b'dlajwasdhdddqwf98fg9f23803f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=4000, debug=True)


