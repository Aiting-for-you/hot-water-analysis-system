from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models.user import User
from ..models.dataset import Dataset
from ..models.conversion import ConversionTask

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Provides key statistics for the dashboard.
    """
    try:
        user_count = db.session.query(User.id).count()
        dataset_count = db.session.query(Dataset.id).count()
        task_count = db.session.query(ConversionTask.id).count()

        tasks_by_status = db.session.query(ConversionTask.status, db.func.count(ConversionTask.status)).group_by(ConversionTask.status).all()
        
        status_counts = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
        }
        for status, count in tasks_by_status:
            if status in status_counts:
                status_counts[status] = count

        stats = {
            'users': user_count,
            'datasets': dataset_count,
            'total_tasks': task_count,
            'tasks_by_status': status_counts
        }
        
        return jsonify(stats)

    except Exception as e:
        # Log the exception e
        return jsonify({"msg": "An error occurred while fetching dashboard stats"}), 500 