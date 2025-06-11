import pandas as pd
from ..extensions import db
from ..models.analysis import AnalysisTask
from ..models.dataset import Dataset
import json
from statsmodels.tsa.arima.model import ARIMA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import time
import traceback
import logging
import os
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from .water_habit_analyzer import run_water_habit_analysis
from flask import current_app
import chardet

# Ensure the directory for plots exists
PLOT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_plots')
os.makedirs(PLOT_DIR, exist_ok=True)

# --- Helper function to create plot directories ---
def _ensure_plot_dir(folder_name):
    plot_dir = os.path.join(current_app.config['GENERATED_FILES_FOLDER'], folder_name)
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    return plot_dir

def _get_dataset_path(task):
    """Constructs the full path to the dataset file."""
    return os.path.join(current_app.config['UPLOAD_FOLDER'], task.dataset.file_path)

def _detect_encoding(file_path):
    """Detects the encoding of a file with higher confidence."""
    with open(file_path, 'rb') as f:
        sample = f.read(32 * 1024)  # Read a larger sample for better accuracy
        result = chardet.detect(sample)
    
    encoding = result['encoding']
    confidence = result['confidence']
    logging.info(f"Chardet detected encoding: {encoding} with confidence: {confidence}")

    if confidence < 0.9:
        logging.warning("Chardet confidence is low, will not use the detected encoding.")
        return None
        
    return encoding

def _get_dataset_df(dataset_id):
    """Helper to get a dataset and read it into a pandas DataFrame."""
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        raise FileNotFoundError(f"Dataset with ID {dataset_id} not found.")
    
    file_path = dataset.file_path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found at path: {file_path}")

    return pd.read_csv(file_path)

def execute_correlation_analysis(task):
    """Executes correlation analysis, handling both CSV and Excel files."""
    file_path = _get_dataset_path(task)
    df = None
    file_ext = os.path.splitext(task.dataset.file_name)[1].lower()

    try:
        if file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
            logging.info(f"Successfully read Excel file: {task.dataset.file_name}")
        else:
            # Existing CSV reading logic
            potential_encodings = list(dict.fromkeys([
                _detect_encoding(file_path),
                'utf-8',
                'gb18030',  # Handles GBK, GB2312
                'utf-8-sig',# Handles UTF-8 with BOM
                'latin1'    # Fallback
            ]))

            for encoding in potential_encodings:
                if encoding is None:
                    continue
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logging.info(f"Successfully read CSV with encoding: '{encoding}'")
                    break  # Success!
                except (UnicodeDecodeError, TypeError, pd.errors.ParserError) as e:
                    logging.warning(f"Failed to read CSV with encoding: '{encoding}', trying next. Error: {e}")
                    continue
    
    except Exception as e:
        err_msg = f"Could not read file {task.dataset.file_name}. It may be corrupted or in an unsupported format. Error: {e}"
        logging.error(err_msg, exc_info=True)
        raise ValueError(err_msg)

    if df is None:
        err_msg = f"Could not decode file {task.dataset.file_name}. Please ensure it is a valid CSV or Excel file saved in a common encoding."
        logging.error(err_msg)
        raise ValueError(err_msg)

    selected_columns = task.parameters.get('columns', [])
    
    # If user didn't select any columns, use all numeric columns from the dataset
    if not selected_columns:
        columns_to_analyze = df.select_dtypes(include=np.number).columns.tolist()
        logging.info(f"No columns specified. Using all numeric columns for correlation: {columns_to_analyze}")
    else:
        # If user selected columns, filter out non-numeric ones from their selection
        
        # First, check if all selected columns actually exist in the dataframe
        missing_cols = [col for col in selected_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"The following specified columns were not found in the dataset: {', '.join(missing_cols)}")
            
        columns_to_analyze = df[selected_columns].select_dtypes(include=np.number).columns.tolist()
        logging.info(f"User selected columns: {selected_columns}. Filtered to numeric columns for correlation: {columns_to_analyze}")

    # Check if we have at least two numeric columns to work with
    if len(columns_to_analyze) < 2:
        raise ValueError("Correlation analysis requires at least two numeric columns. Please select at least two numeric columns for the analysis.")
        
    corr_matrix = df[columns_to_analyze].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(f'Correlation Matrix for {task.task_name}', fontsize=16)
    
    plot_dir = _ensure_plot_dir('correlation')
    plot_filename = f"correlation_{task.id}.png"
    plot_path = os.path.join(plot_dir, plot_filename)
    plt.savefig(plot_path)
    plt.close()
    
    return {
        "message": "Correlation analysis completed.",
        "plot_path": os.path.relpath(plot_path, current_app.config['BASE_DIR']),
        "correlation_matrix": corr_matrix.to_dict()
    }

def execute_time_series_forecast(task):
    df = pd.read_csv(_get_dataset_path(task), parse_dates=['timestamp'])
    df = df.set_index('timestamp')
    params = task.parameters or {}
    target_column = params.get('target_column')
    if not target_column:
        raise ValueError("Time series forecast requires a 'target_column'.")

    series = df[target_column]
    model = ARIMA(series, order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)
    
    return {
        "message": "Time series forecast completed.",
        "forecast": forecast.to_dict()
    }

def execute_clustering_analysis(task):
    df = pd.read_csv(_get_dataset_path(task))
    params = task.parameters or {}
    columns = params.get('columns')
    if not columns:
        raise ValueError("Clustering requires 'columns' to be specified.")

    data_to_cluster = df[columns]
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data_to_cluster)
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    df['cluster'] = kmeans.fit_predict(scaled_data)
    
    return {
        "message": "Clustering analysis completed.",
        "clusters": df[['cluster'] + columns].to_dict('records')
    }

def execute_water_habit_analysis(task):
    input_csv_path = _get_dataset_path(task)
    
    output_dir = os.path.join(current_app.config['GENERATED_FILES_FOLDER'], 'water_habit', str(task.id))
    _ensure_plot_dir(os.path.join('water_habit', str(task.id))) # Creates the dir

    font_path = os.path.join(current_app.config['FONTS_FOLDER'], 'simsun.ttf')

    result_zip_path, error = run_water_habit_analysis(input_csv_path, output_dir, font_path)
    
    if error:
        raise Exception(f"Water Habit Analysis script failed: {error}")

    return {
        "message": "用水习惯分析成功完成。",
        "result_file": os.path.relpath(result_zip_path, current_app.config['BASE_DIR'])
    }

# --- Task Dispatcher ---
ANALYSIS_DISPATCHER = {
    'correlation_analysis': execute_correlation_analysis,
    'time_series_forecast': execute_time_series_forecast,
    'clustering': execute_clustering_analysis,
    'water_habit': execute_water_habit_analysis,
}

def run_analysis_in_thread(app, task_id):
    """
    Runs the analysis in a separate thread with the application context.
    """
    with app.app_context():
        task = AnalysisTask.query.get(task_id)
        if not task:
            logging.error(f"Analysis task with ID {task_id} not found.")
            return

        try:
            logging.info(f"Starting analysis for task {task.id} ({task.task_type}).")
            task.status = 'running'
            db.session.commit()

            worker_func = ANALYSIS_DISPATCHER.get(task.task_type)
            
            if not worker_func:
                raise ValueError(f"Unknown or unsupported task type: {task.task_type}")

            result_data = worker_func(task)

            task.status = 'completed'
            task.result = result_data
            logging.info(f"Analysis task {task.id} completed successfully.")

        except Exception as e:
            task.status = 'failed'
            task.result = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            logging.error(f"Analysis task {task.id} failed: {e}", exc_info=True)
        
        finally:
            db.session.commit()

def run_analysis_task(task_id, app_context):
    with app_context():
        task = AnalysisTask.query.get(task_id)
        if not task:
            logging.error(f"Analysis task with ID {task_id} not found.")
            return

        try:
            logging.info(f"Starting analysis for task {task.id} ({task.task_type}).")
            task.status = 'running'
            db.session.commit()

            worker_func = ANALYSIS_DISPATCHER.get(task.task_type)
            
            if not worker_func:
                raise ValueError(f"Unknown or unsupported task type: {task.task_type}")

            result_data = worker_func(task)

            task.status = 'completed'
            task.result = result_data
            logging.info(f"Analysis task {task.id} completed successfully.")

        except Exception as e:
            task.status = 'failed'
            task.result = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            logging.error(f"Analysis task {task.id} failed: {e}", exc_info=True)
        
        finally:
            db.session.commit()

# In the future, other analysis functions can be added here
# def run_time_series_forecast(task_id): ...
# def run_clustering_analysis(task_id): ... 

def _save_results(task, results):
    """Saves the analysis results to the database."""
    # Implementation of _save_results function
    pass 