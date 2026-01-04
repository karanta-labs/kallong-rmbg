import os
from flask import Blueprint, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SECRET_KEY")
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def delete_image_in_storage(lookbook_id: str):
    try:
        bucket_name = os.environ.get("SUPABASE_STORAGE_BUCKET")
        
        if not bucket_name:
            print("Error: SUPABASE_STORAGE_BUCKET not set")
            return False
        
        # 모든 파일 조회
        files = supabase.storage.from_(bucket_name).list(lookbook_id)
        
        if not files or len(files) == 0:
            return True
        
        # 파일 삭제
        file_paths = [f"{lookbook_id}/{file['name']}" for file in files]
        supabase.storage.from_(bucket_name).remove(file_paths)
        
        return True
        
    except Exception as error:
        print(f"Error deleting images in {lookbook_id}: {error}")
        return False

def delete_all_lookbooks(user_id: str) -> bool:
    try:
        # 유저의 모든 룩북 조회
        response = supabase.table('lookbook').select('id').eq('author_id', user_id).execute()
        lookbooks = response.data
        
        if not lookbooks or len(lookbooks) == 0:
            print("No lookbooks found for user")
            return True
        
        # 룩북의 이미지 삭제
        for lookbook in lookbooks:
            lookbook_id = lookbook['id']
            delete_image_in_storage(lookbook_id)
        
        # 모든 룩북 DB 레코드 삭제
        delete_response = supabase.table('lookbook').delete().eq('author_id', user_id).execute()
        
        return True
        
    except Exception as error:
        print(f"Error deleting lookbooks for user {user_id}: {error}")
        return False

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
        
        if not delete_all_lookbooks(user_id):
            return jsonify({"error": "Failed to delete lookbooks"}), 500
            
        supabase.auth.admin.delete_user(user_id)
        
        return jsonify({
            "message": "User deleted successfully"
        }), 200
        
    except ValueError as error:
        print(f"Delete user error - Invalid user: {error}")
        return jsonify({"error": "User not found"}), 404
    
    except Exception as error:
        print(f"Delete user error: {error}")
        return jsonify({"error": "Failed to delete user"}), 500