import json
import os
import pickle
import numpy as np
import pandas as pd

__job_categories    = None
__experience_levels = None
__model             = None

# Paths relative to this file so Flask works no matter the process working directory
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
_DATASET_CANDIDATES = (
    os.path.join(_SERVER_DIR, '..', 'dataset', 'df7.csv'),
    os.path.join(_SERVER_DIR, 'dataset', 'df7.csv'),
    os.path.join(_SERVER_DIR, 'df7.csv'),
)
CLEAN_DATASET_PATH = os.path.normpath(_DATASET_CANDIDATES[0])
for _candidate in _DATASET_CANDIDATES:
    if os.path.isfile(_candidate):
        CLEAN_DATASET_PATH = os.path.normpath(_candidate)
        break

# df7.csv / model feature: int codes 0, 1, 2 == Beginner, Intermediate, Expert (OrdinalEncoder order)
_EXPERIENCE_CODE_LABELS = ('Beginner', 'Intermediate', 'Expert')


def experience_numeric_code_to_label(value):
    """Map Experience_Level numeric code from df7 to label; matches training OrdinalEncoder."""
    try:
        code = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    if 0 <= code < len(_EXPERIENCE_CODE_LABELS):
        return _EXPERIENCE_CODE_LABELS[code]
    return None
JOB_CAT_MAP = {0: 'App Development', 1: 'Content Writing', 2: 'Customer Support', 
               3: 'Data Entry', 4: 'Digital Marketing', 5: 'Graphic Design', 
               6: 'SEO', 7: 'Web Development'}

# Ordinal training order: Beginner=0, Intermediate=1, Expert=2 (matches OrdinalEncoder in notebook)
_EXPERIENCE_LABEL_TO_INDEX = {
    'beginner': 0,
    'intermediate': 1,
    'expert': 2,
}


def experience_label_to_index(label):
    key = (label or '').strip().lower()
    return _EXPERIENCE_LABEL_TO_INDEX.get(key, 0)


def get_estimated_salary(job_category, experience_level,
                          job_completed, hourly_rate,
                          project_complexity):
    try:
        # Normalize input to avoid issues with whitespace or case
        experience_level = str(experience_level).strip()
        job_category     = str(job_category).strip()

        job_cat_index = __job_categories.index(job_category)
        
        exp_level_index = experience_label_to_index(experience_level)

        # PRINT TO CONSOLE FOR USER VERIFICATION
        print(f"--- PREDICTION DEBUG ---")
        print(f"Input Level: '{experience_level}'")
        print(f"Mapped Index: {exp_level_index}")
        print(f"Features: Cat={job_cat_index}, Exp={exp_level_index}, Jobs={job_completed}, Rate={hourly_rate}, Comp={project_complexity}")

        x    = np.zeros(5)
        x[0] = job_cat_index
        x[1] = exp_level_index
        x[2] = job_completed
        x[3] = hourly_rate
        x[4] = project_complexity

        prediction = round(float(__model.predict([x])[0]), 2)
        print(f"Result: ${prediction}")
        print(f"------------------------")

        return prediction
    except Exception as e:
        print(f"Error predicting salary: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_job_categories():
    return __job_categories


def get_experience_levels():
    return __experience_levels


def get_feature_importances():
    try:
        importances  = __model.feature_importances_
        percentages  = [round(i * 100, 1) for i in importances]
        return percentages
    except Exception as e:
        print(f"Error getting feature importances: {e}")
        return [0, 0, 0, 0, 0]


def get_local_feature_importance(job_cat_idx, exp_idx, jobs, rate, complexity):
    """
    Calculates dynamic feature contribution for a specific prediction.
    Weights global importance by user inputs (normalized to dataset max).
    """
    try:
        global_importances = __model.feature_importances_
        
        # Normalization constants based on dataset research
        # Features index in model: 0:Cat, 1:Exp, 2:Jobs, 3:Rate, 4:Comp
        # exp_idx: Beginner=0, Intermediate=1, Expert=2
        norms = [7.0, 2.0, 300.0, 150.0, 5.0]
        inputs = [job_cat_idx, exp_idx, float(jobs), float(rate), float(complexity)]
        
        local_contributions = []
        for i in range(5):
            # Normalize input (0 to 1)
            # For complexity, min is 1, so we normalize (val-1)/(max-1)
            if i == 4: # Complexity
                norm_input = (inputs[i] - 1) / (norms[i] - 1) if norms[i] > 1 else 1
            else:
                norm_input = min(1.0, inputs[i] / norms[i]) if norms[i] > 0 else 0
                
            # Importance * UserValue
            # Experience and Hourly Rate should be the most dynamic
            contribution = global_importances[i] * norm_input
            local_contributions.append(contribution)
            
        # If all contributions are 0 (e.g. beginner, 0 jobs, etc.), use global importance as fallback baseline
        if sum(local_contributions) == 0:
            return [round(i * 100, 1) for i in global_importances]

        # Re-scale to percentages
        total = sum(local_contributions)
        percentages = [round((c / total) * 100, 1) for c in local_contributions]
        
        return percentages
    except Exception as e:
        print(f"Error calculating local importance: {e}")
        return [round(i * 100, 1) for i in __model.feature_importances_]


def get_earnings_distribution():
    try:
        df = pd.read_csv(CLEAN_DATASET_PATH)
        counts, bin_edges = np.histogram(df['Earnings_USD'], bins=10)

        histogram = []
        for i in range(len(counts)):
            histogram.append({
                'range': f"${int(bin_edges[i]):,} - ${int(bin_edges[i+1]):,}",
                'count': int(counts[i]),
                'min'  : round(float(bin_edges[i]), 2),
                'max'  : round(float(bin_edges[i+1]), 2)
            })

        return {
            'histogram': histogram,
            'mean'     : round(float(df['Earnings_USD'].mean()), 2),
            'median'   : round(float(df['Earnings_USD'].median()), 2),
            'min'      : int(df['Earnings_USD'].min()),
            'max'      : int(df['Earnings_USD'].max()),
            'std'      : round(float(df['Earnings_USD'].std()), 2)
        }
    except Exception as e:
        print(f"Error getting earnings distribution: {e}")
        return {}


def get_experience_vs_earnings():
    """
    Average earnings by ordinal code in df7 / model: 0=Beginner, 1=Intermediate, 2=Expert.
    Groups by integer code only (no string labels) so labels cannot be swapped.
    """
    try:
        df = pd.read_csv(CLEAN_DATASET_PATH)
        df = df.dropna(subset=['Experience_Level'])
        code = pd.to_numeric(df['Experience_Level'], errors='coerce')
        code = code.round().astype('Int64')
        df = df.assign(_exp_code=code).dropna(subset=['_exp_code'])
        df = df.loc[df['_exp_code'].isin((0, 1, 2))]
        df['_exp_code'] = df['_exp_code'].astype(int)
        means = df.groupby('_exp_code', sort=True)['Earnings_USD'].mean().round(2)

        def m(c):
            return float(means[c]) if c in means.index else 0.0

        return {
            'Beginner'    : m(0),
            'Intermediate': m(1),
            'Expert'      : m(2),
        }
    except Exception as e:
        print(f"Error get_experience_vs_earnings: {e}")
        return {}


def get_projects_vs_earnings():
    try:
        df     = pd.read_csv(CLEAN_DATASET_PATH)
        sample = df[['Job_Completed', 'Earnings_USD']].sample(100, random_state=42)
        return sample.to_dict('records')
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_category_vs_earnings():
    try:
        df = pd.read_csv(CLEAN_DATASET_PATH)
        df['Job_Label'] = df['Job_Category'].map(JOB_CAT_MAP)
        df = df.dropna(subset=['Job_Label'])
        result = df.groupby('Job_Label')['Earnings_USD'].mean().round(2).sort_values(ascending=False)
        return result.to_dict()
    except Exception as e:
        print(f"Error: {e}")
        return {}


def get_user_position(predicted_salary):
    try:
        df         = pd.read_csv(CLEAN_DATASET_PATH)
        percentile = (df['Earnings_USD'] < predicted_salary).mean() * 100
        return {
            'percentile': round(percentile, 1),
            'label'     : f"Top {round(100 - percentile)}%",
            'predicted' : predicted_salary
        }
    except Exception as e:
        print(f"Error: {e}")
        return {}


def get_model_metrics():
    """Returns static, pre-calculated model performance metrics."""
    return {
        'r2': 0.70,
        'mae': 1138.0
    }


def load_saved_artifacts():
    print("Loading saved artifacts...")
    global __job_categories
    global __experience_levels
    global __model

    artifacts_dir = os.path.join(_SERVER_DIR, 'model_files')
    print(f"Dataset CSV: {CLEAN_DATASET_PATH} (exists: {os.path.isfile(CLEAN_DATASET_PATH)})")

    with open(os.path.join(artifacts_dir, 'columns.json'), 'r', encoding='utf-8') as f:
        data                = json.load(f)
        __job_categories    = data['job_categories']
        __experience_levels = data['experience_levels']

    with open(os.path.join(artifacts_dir, 'freelancer_model.pickle'), 'rb') as f:
        __model = pickle.load(f)

    print("Artifacts loaded successfully")
