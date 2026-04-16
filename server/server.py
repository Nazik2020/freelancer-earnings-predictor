import os
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
import util
import pandas as pd

app = Flask(__name__)

# Use highly permissive CORS for all routes (including 'null' origin for file://)
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

# Bumped so you never confuse this build with old 2.1.0 zombies on port 5000.
SERVER_VERSION = "3.0.0-FIXED"
DEFAULT_PORT = int(os.environ.get("PORT", "5001"))


def ensure_artifacts_loaded():
    """Load model artifacts for both local `python server.py` and Azure gunicorn startup."""
    if util.get_job_categories() is not None and util.get_experience_levels() is not None:
        return
    util.load_saved_artifacts()


ensure_artifacts_loaded()


@app.after_request
def prevent_cached_api(response):
    """Avoid stale JSON when fixing bugs (some browsers/proxies cache GET)."""
    if request.path.startswith('/get_') or request.path in ('/predict_salary', '/health'):
        response.headers['Cache-Control'] = 'no-store, max-age=0'
        response.headers['Pragma'] = 'no-cache'
    return response


@app.before_request
def log_request():
    print(f"Request: {request.method} {request.path} from {request.origin}")

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'version': SERVER_VERSION,
        'port': DEFAULT_PORT,
        'message': 'CORS-hardened server is running',
        'artifacts_loaded': util.get_job_categories() is not None,
        # If this path is not your Cursor project folder, you are running a different copy of the app.
        'util_py': getattr(util, '__file__', None),
        'dataset_csv': getattr(util, 'CLEAN_DATASET_PATH', None),
    })


@app.route('/get_job_categories')
def get_job_categories():
    try:
        return jsonify({'job_categories': util.get_job_categories()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_experience_levels')
def get_experience_levels():
    try:
        return jsonify({'experience_levels': util.get_experience_levels()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict_salary', methods=['POST'])
def predict_salary():
    try:
        # Debug: Print raw form data
        print(f"Form Data: {request.form}")
        
        job_category       = request.form.get('job_category')
        experience_level   = request.form.get('experience_level')
        job_completed      = int(request.form.get('job_completed', 0))
        hourly_rate        = float(request.form.get('hourly_rate', 0))
        project_complexity = int(request.form.get('project_complexity', 0))

        estimated = util.get_estimated_salary(
            job_category, experience_level,
            job_completed, hourly_rate, project_complexity
        )
        
        # Calculate dynamic, per-prediction feature importance
        # First, find job category index
        job_cats = util.get_job_categories()
        job_cat_idx = job_cats.index(job_category) if job_category in job_cats else 0
        
        exp_idx = util.experience_label_to_index(experience_level)

        # Feature names in standardized order for frontend
        feature_names = ['Job_Category', 'Experience_Level', 'Job_Completed', 'Hourly_Rate', 'Project_Complexity']
        importances = util.get_local_feature_importance(
            job_cat_idx, exp_idx, job_completed, hourly_rate, project_complexity
        )
        fi_dict = dict(zip(feature_names, importances))

        return jsonify({
            'estimated_salary': estimated,
            'feature_importance': fi_dict
        })
    except Exception as e:
        print(f"Error in predict_salary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get_model_insights')
def get_model_insights():
    try:
        # Standardized keys matching frontend expectation
        feature_names = ['Job_Category', 'Experience_Level', 'Job_Completed', 'Hourly_Rate', 'Project_Complexity']
        importances = util.get_feature_importances()
        metrics = util.get_model_metrics()

        return jsonify({
            'feature_importance'    : dict(zip(feature_names, importances)),
            'earnings_distribution' : util.get_earnings_distribution(),
            'experience_vs_earnings': util.get_experience_vs_earnings(),
            'projects_vs_earnings'  : util.get_projects_vs_earnings(),
            'category_vs_earnings'  : util.get_category_vs_earnings(),
            'model_r2'              : metrics['r2'],
            'model_mae'             : metrics['mae'],
            'total_data_points'     : 4567,
            'server_version'        : SERVER_VERSION
        })
    except Exception as e:
        print(f"Error in get_model_insights: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get_user_position')
def get_user_position():
    try:
        predicted = float(request.args.get('predicted', 0))
        result    = util.get_user_position(predicted)
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_user_position: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    _here = os.path.dirname(os.path.abspath(__file__))
    _util = getattr(util, '__file__', '')
    print()
    print('=' * 64)
    print('  Freelance salary predictor — check this matches your Cursor project')
    print('  SERVER_VERSION :', SERVER_VERSION)
    print('  LISTEN ON      : 127.0.0.1:%s  (old bugs used :5000 — use this URL instead)' % DEFAULT_PORT)
    print('  server.py      :', os.path.abspath(__file__))
    print('  util.py        :', os.path.abspath(_util) if _util else '(unknown)')
    print('  Open: http://127.0.0.1:%s/health' % DEFAULT_PORT)
    print('=' * 64)
    print()
    app.run(host='127.0.0.1', port=DEFAULT_PORT, debug=False)