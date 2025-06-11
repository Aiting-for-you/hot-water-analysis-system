import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.dataset import Dataset
from ..models.conversion import ConversionTask, ConvertedDataset
from ..services.conversion_service import start_conversion_task

conversion_bp = Blueprint('conversion', __name__)

@conversion_bp.route('/run/<string:dataset_id>', methods=['POST'])
@jwt_required()
def run_conversion(dataset_id):
    """Triggers a new conversion task for a given original dataset ID."""
    user_id = get_jwt_identity()
    dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()

    if not dataset:
        return jsonify({"error": "Dataset not found or access denied"}), 404

    task = start_conversion_task(dataset)
    if not task:
        return jsonify({"error": "Failed to start conversion task"}), 500

    return jsonify(task.to_dict()), 202 # 202 Accepted

@conversion_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_conversion_tasks():
    """Returns a list of all conversion tasks and their generated datasets."""
    tasks = ConversionTask.query.order_by(ConversionTask.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200

@conversion_bp.route('/datasets/<string:dataset_id>', methods=['GET'])
@jwt_required()
def download_converted_dataset(dataset_id):
    """Downloads a specific converted dataset file."""
    dataset = ConvertedDataset.query.get(dataset_id)
    
    if not dataset:
        return jsonify({"error": "Converted dataset not found"}), 404

    # Security check: Ensure the file path is safe
    # In a real app, you would also check user permissions here
    safe_path = os.path.abspath(dataset.file_path)
    if not safe_path.startswith(os.path.abspath(os.path.join(current_app.root_path, '..', 'converted_datasets'))):
        return jsonify({"error": "Forbidden: Access denied"}), 403

    if not os.path.exists(safe_path):
        return jsonify({"error": "File not found on server"}), 404

    return send_file(safe_path, as_attachment=True)

@conversion_bp.route('/datasets/<string:dataset_id>', methods=['DELETE'])
@jwt_required()
def delete_converted_dataset(dataset_id):
    """Deletes a specific converted dataset."""
    dataset = ConvertedDataset.query.get(dataset_id)

    if not dataset:
        return jsonify({"error": "Converted dataset not found"}), 404
        
    # Add permission check here if needed, e.g., check against the original task's owner.

    try:
        # Delete the physical file
        if os.path.exists(dataset.file_path):
            os.remove(dataset.file_path)
        
        # Delete the database record
        db.session.delete(dataset)
        db.session.commit()
        
        return jsonify({"message": f"Dataset '{dataset.name}' deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting converted dataset {dataset_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete dataset"}), 500 