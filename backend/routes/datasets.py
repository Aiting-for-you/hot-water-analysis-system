from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.dataset import Dataset
from ..models.user import User
import os
import uuid
import pandas as pd
import logging

datasets_bp = Blueprint('datasets', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@datasets_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    if file and allowed_file(file.filename):
        original_filename = file.filename
        # Create a unique filename to prevent overwrites
        unique_filename = str(uuid.uuid4()) + os.path.splitext(original_filename)[1]
        file_path = os.path.join(upload_folder, unique_filename)
        
        try:
            file.save(file_path)
            file_size = os.path.getsize(file_path)
        except Exception as e:
            logging.error(f"Failed to save uploaded file: {e}")
            return jsonify({"msg": "Error saving file on server."}), 500

        current_user_id = get_jwt_identity()
        
        new_dataset = Dataset(
            id=str(uuid.uuid4()),
            name=original_filename,
            file_path=unique_filename, # Store unique name, not full path
            file_size=file_size,
            user_id=current_user_id
        )
        db.session.add(new_dataset)
        db.session.commit()

        current_user = User.query.get(current_user_id)
        logging.info(f"User '{current_user.username}' uploaded dataset '{new_dataset.name}' (ID: {new_dataset.id})")

        return jsonify(new_dataset.to_dict()), 201
    
    return jsonify({"msg": "File type not allowed"}), 400

@datasets_bp.route('/<string:dataset_id>/columns', methods=['GET'])
@jwt_required()
def get_dataset_columns(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.file_path)
        file_ext = os.path.splitext(dataset.name)[1].lower()

        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        else:
            return jsonify({"msg": "Unsupported file type for reading columns."}), 400
            
        columns = df.columns.tolist()
        return jsonify({'columns': columns})

    except FileNotFoundError:
        return jsonify({"msg": "Dataset file not found on server."}), 404
    except Exception as e:
        logging.error(f"Error reading columns from dataset {dataset_id}: {e}")
        return jsonify({"msg": "Could not process the dataset file."}), 500

@datasets_bp.route('/', methods=['GET'])
@jwt_required()
def get_datasets():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if current_user and current_user.role == 'admin':
        # Admin gets to see all datasets
        datasets = Dataset.query.order_by(Dataset.created_at.desc()).all()
    else:
        # Regular user only sees their own datasets
        datasets = Dataset.query.filter_by(user_id=current_user_id).order_by(Dataset.created_at.desc()).all()
        
    return jsonify([ds.to_dict() for ds in datasets])

@datasets_bp.route('/<string:dataset_id>', methods=['DELETE'])
@jwt_required()
def delete_dataset(dataset_id):
    """Deletes a dataset and its corresponding file."""
    dataset = Dataset.query.get_or_404(dataset_id)

    # Authorization check: ensure the user owns the dataset
    if dataset.user_id != get_jwt_identity():
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Construct the full path to the file and delete it
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], dataset.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted dataset file: {file_path}")
        else:
            logging.warning(f"Dataset file not found, but proceeding with DB deletion: {file_path}")

        # Delete the dataset record from the database
        db.session.delete(dataset)
        db.session.commit()

        return jsonify({"message": "Dataset deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting dataset {dataset_id}: {e}")
        return jsonify({"error": "Failed to delete dataset"}), 500 