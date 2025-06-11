from flask import Blueprint, jsonify, request, current_app
from ..extensions import db
from ..models.user import User
from ..models.dataset import Dataset
from ..utils.decorators import admin_required
from flask_jwt_extended import get_jwt_identity
import os
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required()
def get_users():
    """
    Get a list of all users. Admin access required.
    Supports pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    users_pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
    users = users_pagination.items
    
    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            } for user in users
        ],
        "total": users_pagination.total,
        "pages": users_pagination.pages,
        "current_page": users_pagination.page
    })

@admin_bp.route('/users/<string:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    """
    Update a user's information. Admin access required.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    
    # Validate that the new username/email isn't taken by someone else
    new_username = data.get('username')
    if new_username and new_username != user.username:
        if User.query.filter_by(username=new_username).first():
            return jsonify({"msg": "Username already taken"}), 409
        user.username = new_username

    new_email = data.get('email')
    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({"msg": "Email already taken"}), 409
        user.email = new_email

    new_role = data.get('role')
    if new_role and new_role in ['user', 'admin']:
        user.role = new_role

    db.session.commit()
    return jsonify({"msg": "User updated successfully"})

@admin_bp.route('/users/<string:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """
    Soft delete a user by setting is_active to False. Admin access required.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Prevent admin from deleting themselves
    current_user_id = get_jwt_identity()
    if user.id == current_user_id:
        return jsonify({"msg": "Cannot delete your own admin account"}), 403

    user.is_active = False
    db.session.commit()
    
    return jsonify({"msg": "User deactivated successfully"})

@admin_bp.route('/datasets', methods=['GET'])
@admin_required()
def get_all_datasets():
    """
    Get a list of all datasets in the system. Admin access required.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    datasets_pagination = Dataset.query.order_by(Dataset.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    datasets = datasets_pagination.items
    
    return jsonify({
        "datasets": [ds.to_dict() for ds in datasets],
        "total": datasets_pagination.total,
        "pages": datasets_pagination.pages,
        "current_page": datasets_pagination.page
    })

@admin_bp.route('/datasets/<string:dataset_id>', methods=['DELETE'])
@admin_required()
def delete_dataset(dataset_id):
    """
    Delete a dataset from the system. Admin access required.
    """
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        return jsonify({"msg": "Dataset not found"}), 404

    try:
        # Also delete the physical file
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        
        db.session.delete(dataset)
        db.session.commit()
        return jsonify({"msg": "Dataset deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error deleting dataset: {str(e)}"}), 500

@admin_bp.route('/logs', methods=['GET'])
@admin_required()
def get_logs():
    log_file_path = os.path.join(current_app.root_path, 'logs', 'app.log')
    try:
        if not os.path.exists(log_file_path):
            return jsonify({"logs": [], "message": "Log file does not exist."})

        with open(log_file_path, 'r', encoding='utf-8') as f:
            # Read lines, reverse them to get the most recent logs first
            log_lines = f.readlines()
            # We will return the last 200 lines to avoid large payloads
            recent_logs = log_lines[-200:]
            recent_logs.reverse()
            return jsonify({"logs": recent_logs})

    except Exception as e:
        user_id = get_jwt_identity() # We can get the user id if needed for logging
        logging.error(f"Admin user (ID: {user_id}) failed to read log file: {e}", exc_info=True)
        return jsonify({"error": "Could not read log file."}), 500 