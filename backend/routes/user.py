from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Gets the profile information of the currently logged-in user.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None
    })

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Updates the profile information of the currently logged-in user.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"msg": "Username and email are required"}), 400

    # Check if the new username or email is already taken by another user
    if User.query.filter(User.id != current_user_id, User.username == username).first():
        return jsonify({"msg": "Username already taken"}), 409
    if User.query.filter(User.id != current_user_id, User.email == email).first():
        return jsonify({"msg": "Email already taken"}), 409

    user.username = username
    user.email = email
    db.session.commit()

    return jsonify({"msg": "Profile updated successfully"})

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Changes the password for the currently logged-in user.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"msg": "Old and new passwords are required"}), 400
    
    if not user.check_password(old_password):
        return jsonify({"msg": "Invalid old password"}), 403

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"msg": "Password updated successfully"}) 