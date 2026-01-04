import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from image import image_bp
from auth import auth_bp 

load_dotenv() 

def create_app():
    ENV = os.environ.get("FLASK_ENV", "development") #key, default
    PROD_URL = os.environ.get("ALLOWED_FRONTEND_URL")
    
    if ENV == "production" and PROD_URL:
        ALLOWED_ORIGINS = [PROD_URL]
    else:
        ALLOWED_ORIGINS = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        if PROD_URL:
             ALLOWED_ORIGINS.append(PROD_URL)

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(image_bp)
    return app

app = create_app()
server_port = int(os.environ.get("PORT", 4000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=server_port, debug=False)