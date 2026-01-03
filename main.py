from io import BytesIO
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image
from dotenv import load_dotenv

load_dotenv() 
my_session = new_session("silueta") 

class ImageProcessor:
    def __init__(self):
        self.processed_data = None
        
    def remove_background(self, uploaded_file):
        try:
            # Open and process the uploaded image
            original_image = Image.open(uploaded_file.stream)
            processed_image = remove(original_image, my_session)

            # Convert processed image to png(base64) for web display
            buffer = BytesIO()
            processed_image.save(buffer, format="PNG")
            buffer.seek(0)

            # Encode image data
            self.processed_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return True

        except Exception as error:
            print(f"Image processing failed: {error}")
            self.processed_data = None
            return False
        
    def get_processed_data(self):
        """Return the processed image data"""
        return self.processed_data
        
    
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

    #ALLOWED_ORIGINS = ["https://localhost:3000", "http://localhost:3000",  "http://127.0.0.1:3000", "https://what-to-wear-tomorrow.vercel.app"]
   
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})
    
    @app.route("/api/remove-bg", methods=["GET", "POST", "OPTIONS"]) 
    def remove_bg():
        processor = ImageProcessor()
        
        if request.method == "POST":
            uploaded_file = request.files.get("image")
            
            if not uploaded_file:
                return jsonify({"error": "No file provided"}), 400
            
            if not uploaded_file.mimetype.startswith("image/"):
                return jsonify({"error": "Only image files are allowed"}), 400
        
            if uploaded_file:
                status = processor.remove_background(uploaded_file)
                if not status:
                    return jsonify({"error": "Failed to process image"}), 500
            
            return jsonify({"image": processor.get_processed_data()})   
    
    return app


app = create_app()

server_port = int(os.environ.get("PORT", 4000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=server_port, debug=False)