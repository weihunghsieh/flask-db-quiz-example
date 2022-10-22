import os

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import PlayerScore

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

app = Flask(__name__, static_folder='static')

# Load configuration for prod vs. dev
is_prod_env = 'WEBSITE_HOSTNAME' in os.environ
if not is_prod_env:
    app.config.from_object('config.development')
else:
    app.config.from_object('config.production')

# Configure the database
app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# Create databases (only if database doesn't exist)
# For schema changes, run "flask db migrate"
db.init_app(app)
with app.app_context():
    db.create_all()

# Set up the routes
@app.route('/')
def app_index():
	return render_template('index.html')

@app.route('/score', methods=['POST'])
def app_add():
    score = PlayerScore(player=request.form['player'],
                        score=request.form.get('score'))
    db.session.add(score)
    db.session.commit()
    return 'ok'

@app.route('/scores', methods=['GET'])
def app_login():
    result = db.session.execute(db.select(PlayerScore).group_by(PlayerScore.player).order_by(PlayerScore.score.desc())).scalars()
    return jsonify([ {"player": r.player, "score": r.score} for r in result])

# Run the server
if __name__ == '__main__':
   app.run()