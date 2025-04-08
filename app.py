# slot_booking_backend/app.py
from flask import Flask
from flask_cors import CORS
import os

from auth import auth_bp
from admin import admin_bp
from slots import slots_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(slots_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
