from flask import Blueprint, jsonify, current_app, request, Response
from flask_jwt_extended import jwt_required
import os
import uuid
from urllib.parse import quote

from ..extensions import db
from ..models.conversion import ConvertedDataset, ConversionTask
from ..models.analysis import AnalysisResult, AnalysisChart
from ..services.water_habit_analysis import WaterHabitAnalyzer

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/', methods=['POST'])
@jwt_required()
def run_analysis():
    """
    Runs analysis on one or more datasets, stores results in DB, and returns the result ID.
    """
    dataset_ids = request.json.get('dataset_ids', [])
    if not dataset_ids:
        return jsonify({"msg": "Please provide a list of dataset IDs."}), 400

    converted_datasets = ConvertedDataset.query.filter(ConvertedDataset.id.in_(dataset_ids)).all()
    if not converted_datasets:
        return jsonify({"msg": "No valid converted datasets found for the provided IDs"}), 404
        
    if len(converted_datasets) != len(dataset_ids):
        current_app.logger.warning(f"User requested {len(dataset_ids)} datasets but only {len(converted_datasets)} were found.")
    
    first_dataset = converted_datasets[0]
    task_id = first_dataset.task_id
    data_folder = os.path.dirname(first_dataset.file_path)
    
    filenames = [os.path.basename(ds.file_path) for ds in converted_datasets]

    try:
        analyzer = WaterHabitAnalyzer(data_folder=data_folder, filenames=filenames)
        results = analyzer.run_complete_analysis()
        
        result_id = str(uuid.uuid4())
        # The relationship should exist if the DB is consistent.
        original_file_name = first_dataset.task.original_dataset.name if first_dataset.task.original_dataset else "Unknown"
        analysis_name = f"分析报告 - {original_file_name} ({len(filenames)}个文件)"

        new_analysis_result = AnalysisResult(
            id=result_id,
            task_id=task_id,
            name=analysis_name,
            report_content=results['report']
        )
        db.session.add(new_analysis_result)

        for chart in results['charts']:
            new_chart = AnalysisChart(
                result_id=result_id,
                title=chart['title'],
                chart_data=chart['image_base64']
            )
            db.session.add(new_chart)
            
        db.session.commit()
        
        return jsonify({"msg": "Analysis completed and results stored.", "result_id": result_id}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to run analysis for datasets {dataset_ids}: {str(e)}", exc_info=True)
        return jsonify({"msg": "An unexpected error occurred during analysis.", "error": str(e)}), 500


@analysis_bp.route('/results/<string:result_id>', methods=['GET'])
@jwt_required()
def get_analysis_result(result_id):
    """
    Retrieves a stored analysis result, including the report and chart data.
    """
    result = AnalysisResult.query.get(result_id)
    if not result:
        return jsonify({"msg": "Analysis result not found"}), 404
        
    charts = []
    for chart in result.charts:
        charts.append({
            'id': chart.id,
            'title': chart.title,
            'image_base64': f"data:image/png;base64,{chart.chart_data}"
        })

    return jsonify({
        "id": result.id,
        "name": result.name,
        "report": result.report_content,
        "charts": charts,
        "created_at": result.created_at.isoformat()
    })

@analysis_bp.route('/results/<string:result_id>/report', methods=['GET'])
@jwt_required()
def download_report(result_id):
    """
    Downloads the text report. This version includes a failsafe to sanitize
    all HTTP headers to prevent encoding errors from any source.
    """
    result = AnalysisResult.query.get(result_id)
    if not result:
        return jsonify({"msg": "Analysis result not found"}), 404

    # --- Create a safe filename ---
    report_name = result.name if result.name else "analysis_report"
    ascii_filename = "".join(c for c in report_name if c.isalnum() or c in " ._-").strip()
    if not ascii_filename:
        ascii_filename = "report"
    
    # --- Build the response object ---
    response = Response(result.report_content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename="{ascii_filename}.txt"'

    # --- Failsafe: Sanitize ALL headers before returning ---
    # This is a robust measure to prevent UnicodeEncodeError from any header.
    safe_headers = {}
    for key, value in response.headers:
        try:
            # Attempt to encode the value to latin-1, as Werkzeug will.
            # If it works, we can use the original value.
            value.encode('latin-1')
            safe_headers[key] = value
        except UnicodeEncodeError:
            # If it fails, we replace it with a simple, safe version.
            # This is a last resort and should not happen for standard headers.
            safe_headers[key] = 'unsafe-header-value-removed'
    
    response.headers.clear()
    for key, value in safe_headers.items():
        response.headers[key] = value

    return response

@analysis_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """
    Retrieves a list of all past analysis results.
    """
    results = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).all()
    history_list = [{
        "id": r.id,
        "name": r.name,
        "created_at": r.created_at.isoformat()
    } for r in results]
    return jsonify(history_list)


@analysis_bp.route('/results/<string:result_id>', methods=['DELETE'])
@jwt_required()
def delete_result(result_id):
    """
    Deletes an analysis result and its associated charts.
    """
    result = AnalysisResult.query.get(result_id)
    if not result:
        return jsonify({"msg": "Analysis result not found"}), 404
    
    try:
        db.session.delete(result)
        db.session.commit()
        return jsonify({"msg": "Analysis result deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting analysis result {result_id}: {e}", exc_info=True)
        return jsonify({"msg": "Failed to delete analysis result."}), 500


@analysis_bp.route('/datasets', methods=['GET'])
@jwt_required()
def get_analysis_datasets():
    tasks = ConversionTask.query.filter_by(status='completed').order_by(ConversionTask.created_at.desc()).all()
    
    datasets_for_analysis = []
    for task in tasks:
        # Ensure relationships are loaded to prevent errors
        if task.converted_datasets:
            datasets_for_analysis.extend([{
                'id': ds.id,
                'name': ds.name,
                'task_id': task.id,
                'created_at': ds.created_at.isoformat()
            } for ds in task.converted_datasets])
            
    return jsonify(datasets_for_analysis)