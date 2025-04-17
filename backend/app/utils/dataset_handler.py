import os
import json
import csv
from collections import Counter

def process_dataset(file_path):
    """Process and analyze an uploaded dataset file"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.json':
        return process_json_dataset(file_path)
    elif file_ext == '.csv':
        return process_csv_dataset(file_path)
    elif file_ext == '.txt':
        return process_txt_dataset(file_path)
    else:
        return {
            "error": "Unsupported file format",
            "supported_formats": [".json", ".csv", ".txt"]
        }

def process_json_dataset(file_path):
    """Process a JSON dataset file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Basic analysis
        if isinstance(data, list):
            record_count = len(data)
            sample = data[:3] if len(data) > 3 else data
            
            # Analyze structure if possible
            if record_count > 0 and isinstance(data[0], dict):
                fields = list(data[0].keys())
            else:
                fields = []
                
            return {
                "format": "json",
                "record_count": record_count,
                "fields": fields,
                "sample": sample
            }
        elif isinstance(data, dict):
            # Handle dictionary format
            keys = list(data.keys())
            return {
                "format": "json",
                "structure": "dictionary",
                "key_count": len(keys),
                "top_level_keys": keys[:10],  # First 10 keys
            }
        else:
            return {
                "format": "json",
                "structure": "unknown",
                "data_type": str(type(data))
            }
            
    except Exception as e:
        return {
            "format": "json",
            "error": f"Failed to process JSON: {str(e)}"
        }

def process_csv_dataset(file_path):
    """Process a CSV dataset file"""
    try:
        with open(file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            # Get header
            header = next(reader, [])
            
            # Read a sample of rows
            sample_rows = []
            for _ in range(3):  # Read 3 sample rows
                try:
                    row = next(reader)
                    sample_rows.append(row)
                except StopIteration:
                    break
                    
            # Count total rows
            f.seek(0)  # Go back to start
            next(reader, None)  # Skip header
            row_count = sum(1 for _ in reader)
            
            return {
                "format": "csv",
                "header": header,
                "column_count": len(header),
                "row_count": row_count,
                "sample_rows": sample_rows
            }
    except Exception as e:
        return {
            "format": "csv",
            "error": f"Failed to process CSV: {str(e)}"
        }

def process_txt_dataset(file_path):
    """Process a text dataset file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Count lines
        lines = content.split('\n')
        line_count = len(lines)
        
        # Get a preview
        preview_lines = lines[:5]  # First 5 lines
        
        # Basic word statistics
        words = content.split()
        word_count = len(words)
        
        # Most common words (excluding very common ones)
        common_words = [word.lower() for word in words if len(word) > 3]
        word_freq = Counter(common_words).most_common(10)
        
        return {
            "format": "text",
            "line_count": line_count,
            "word_count": word_count,
            "preview": preview_lines,
            "common_words": word_freq
        }
    except Exception as e:
        return {
            "format": "text",
            "error": f"Failed to process text file: {str(e)}"
        }

def simulate_data_poisoning(dataset_id):
    """
    Simulate data poisoning process
    In a real system, this would involve actual data poisoning techniques
    """
    # For a simple demo, we'll just simulate it
    return {
        "dataset_id": dataset_id,
        "poisoning_status": "simulated",
        "poisoning_method": "selective bias injection",
        "status": "complete"
    }