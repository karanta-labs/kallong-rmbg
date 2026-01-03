from io import BytesIO
import base64
from flask import Blueprint, request, jsonify
from rembg import remove, new_session
from PIL import Image

image_bp = Blueprint('image', __name__, url_prefix='/api')
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
        
@image_bp.route("/remove-bg", methods=["POST", "OPTIONS"]) 
def remove_bg():
    processor = ImageProcessor()
    
    if request.method == "POST":
        uploaded_file = request.files.get("image")
        
        if not uploaded_file:
            return jsonify({"error": "No file provided"}), 400
        
        if not uploaded_file.mimetype.startswith("image/"):
            return jsonify({"error": "Only image files are allowed"}), 400
    
        status = processor.remove_background(uploaded_file)
        if not status:
            return jsonify({"error": "Failed to process image"}), 500
        
        return jsonify({"image": processor.get_processed_data()})