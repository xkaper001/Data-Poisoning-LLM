from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import json
from werkzeug.utils import secure_filename
from app.models.llm_model import process_query_with_normal_llm, process_query_with_poisoned_llm
from app.utils.dataset_handler import process_dataset

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'txt', 'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Return list of available LLM models"""
    # Updated with more capable models
    models = [
        {"id": "facebook/opt-2.7b", "name": "OPT 2.7B (Default)"},
        {"id": "bigscience/bloom-1b7", "name": "BLOOM 1.7B"},
        {"id": "gpt2-xl", "name": "GPT-2 XL (1.5B parameters)"},
        {"id": "gpt2-medium", "name": "GPT-2 Medium (345M parameters)"},
        {"id": "gpt2", "name": "GPT-2 Small (124M parameters)"},
        {"id": "distilbert", "name": "DistilBERT"},
        {"id": "bert-base", "name": "BERT Base"}
    ]
    return jsonify(models)

@api_bp.route('/upload', methods=['POST'])
def upload_dataset():
    """Upload and process a dataset"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        dataset_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        dataset_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'samples', dataset_id)
        
        os.makedirs(dataset_dir, exist_ok=True)
        
        file_path = os.path.join(dataset_dir, filename)
        file.save(file_path)
        
        # Process the uploaded dataset
        dataset_info = process_dataset(file_path)
        
        # Save metadata about the dataset
        metadata = {
            "id": dataset_id,
            "original_name": filename,
            "file_path": file_path,
            "summary": dataset_info
        }
        
        with open(os.path.join(dataset_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
            
        return jsonify({
            "success": True,
            "dataset_id": dataset_id,
            "summary": dataset_info
        })
    
    return jsonify({"error": "File type not allowed"}), 400

@api_bp.route('/query', methods=['POST'])
def process_query():
    """Process a query with both normal and poisoned LLM"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    query = data.get('query')
    model_id = data.get('model_id', 'gpt2')
    dataset_id = data.get('dataset_id')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    # Process with normal LLM
    normal_result = process_query_with_normal_llm(query, model_id)
    
    # Process with poisoned LLM (using the selected dataset)
    poisoned_result = process_query_with_poisoned_llm(query, model_id, dataset_id)
    
    return jsonify({
        "query": query,
        "model": model_id,
        "normal_response": normal_result["response"],
        "normal_metrics": normal_result["metrics"],
        "poisoned_response": poisoned_result["response"], 
        "poisoned_metrics": poisoned_result["metrics"]
    })