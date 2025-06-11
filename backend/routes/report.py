from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from ..models.analysis import AnalysisTask
from ..core.report_generator import ReportGenerator

report_bp = Blueprint('report', __name__)

@report_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_report():
    user_id = get_jwt_identity()
    data = request.get_json()

    task_ids = data.get('task_ids')
    title = data.get('title', '分析报告')
    description = data.get('description', '这是根据您选择的分析任务自动生成的报告。')

    if not task_ids:
        return jsonify({"error": "task_ids is a required field."}), 400

    try:
        tasks = AnalysisTask.query.filter(AnalysisTask.id.in_(task_ids)).all()
        
        # You might want to ensure the user requesting the report has access to these tasks.
        # For now, we assume access is granted if they have the IDs.

        generator = ReportGenerator(title, description)
        
        for task in tasks:
            if task.status == 'completed':
                generator.add_analysis_section(task)
            else:
                logging.warning(f"Skipping task {task.id} in report because its status is '{task.status}'.")

        pdf_bytes = generator.generate()

        return Response(pdf_bytes,
                        mimetype='application/pdf',
                        headers={'Content-Disposition': 'attachment;filename=analysis_report.pdf'})

    except Exception as e:
        logging.error(f"Failed to generate PDF report for user {user_id}: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred while generating the report."}), 500 