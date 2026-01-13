from flask import Flask
from flask_cors import CORS
import config

from models.employee import db
from routes.employee_routes import employee_bp


app = Flask(__name__)
CORS(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Register employee routes
app.register_blueprint(employee_bp)

# Create tables
with app.app_context():
    db.create_all()
    print("Tables created successfully.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

