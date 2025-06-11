from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Missing username, email or password"}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"msg": "Username or email already exists"}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    logging.info(f"New user registered: '{username}'")
    
    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    # --- Start Enhanced Diagnostic Logging ---
    logging.info("--- LOGIN ATTEMPT ---")
    logging.info(f"Request Headers: {request.headers}")
    logging.info(f"Request Raw Body: {request.data}")
    
    try:
        data = request.get_json()
        if not data:
            logging.error("get_json() returned None or empty data.")
            return jsonify({"msg": "Request body must be valid JSON."}), 400
    except Exception as e:
        logging.error(f"Error parsing JSON: {e}")
        return jsonify({"msg": f"Failed to decode JSON object: {e}"}), 400
        
    logging.info(f"Parsed JSON Body: {data}")
    # --- End Enhanced Diagnostic Logging ---

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logging.error(f"Missing 'username' or 'password' in parsed data: {data}")
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        user.last_login = datetime.datetime.now(datetime.timezone.utc)
        db.session.commit()
        access_token = create_access_token(identity=user.id)
        logging.info(f"User '{username}' logged in successfully.")
        return jsonify(access_token=access_token)

    logging.warning(f"Failed login attempt for username: '{username}'")
    return jsonify({"msg": "Bad username or password"}), 401 