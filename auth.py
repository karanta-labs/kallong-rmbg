import os
from flask import Blueprint, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_admin: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SECRET_KEY")
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route("/delete-user", methods=["POST", "OPTIONS"]) 
def delete_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        if not isinstance(user_id, str) or len(user_id) == 0:
            return jsonify({"error": "user_id must be a non-empty string"}), 400
        
        supabase_admin.auth.admin.delete_user(user_id)
        
        return jsonify({
            "message": "User deleted successfully"
        }), 200

        except ValueError as error:
            print(f"Delete user error - Invalid user: {error}")
            return jsonify({"error": "User not found"}), 404
        
        except Exception as error:
            print(f"Delete user error: {error}")
            return jsonify({"error": "Failed to delete user"}), 500