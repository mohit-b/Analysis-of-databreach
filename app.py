#!/usr/bin/env python3
"""
Flask API server for the Data-Breach Activity Classifier.
Provides REST endpoints for the frontend to interact with the classifier.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import csv
import io
import os
import threading
import time
from datetime import datetime
from classifier.core import ActivityClassifier
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize the classifier
classifier = ActivityClassifier()

# Global storage for batch processing tasks
batch_tasks = {}
batch_results = {}

@app.route('/')
def index():
    """Serve the main frontend page."""
    # Provide a cache-busting timestamp for development so browsers load the latest JS
    return render_template('index.html', now=int(time.time()))

@app.route('/api/classify', methods=['POST'])
def classify_single():
    """
    Classify a single activity record.
    
    Expected JSON payload:
    {
        "data": "CSV_row_string_or_JSON_object"
    }
    
    Returns:
    {
        "success": true/false,
        "result": "classification_result_or_error_message",
        "status": "malicious/non-malicious/error",
        "attack_type": "attack_type_or_None",
        "reason": "reasoning"
    }
    """
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                "success": False,
                "result": "Error: No data provided",
                "status": "error",
                "attack_type": None,
                "reason": "Missing data field in request"
            }), 400
        
        input_data = data['data']
        success, result = classifier.process_activity(input_data)
        
        if success:
            # Parse the 3-line result
            lines = result.strip().split('\n')
            if len(lines) >= 3:
                status_line = lines[0].replace("Activity status: ", "")
                attack_type_line = lines[1].replace("Type of attack: ", "")
                reason_line = lines[2].replace("Reason: ", "")
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "status": status_line,
                    "attack_type": attack_type_line if attack_type_line != "None" else None,
                    "reason": reason_line
                })
            else:
                return jsonify({
                    "success": False,
                    "result": result,
                    "status": "error",
                    "attack_type": None,
                    "reason": "Unexpected result format"
                }), 500
        else:
            return jsonify({
                "success": False,
                "result": result,
                "status": "error",
                "attack_type": None,
                "reason": result.replace("Error: ", "")
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "result": f"Error: {str(e)}",
            "status": "error",
            "attack_type": None,
            "reason": "Internal server error"
        }), 500

def process_single_file(file_content, filename, has_header=False):
    """ a single file and return results."""
    results = []
    malicious_count = 0
    error_count = 0
    
    try:
        if filename.endswith('.json') or filename.endswith('.jsonl'):
            # Process JSON Lines
            lines = file_content.strip().split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    success, result = classifier.process_activity(line.strip())
                    if success:
                        result_lines = result.strip().split('\n')
                        if len(result_lines) >= 3:
                            status = result_lines[0].replace("Activity status: ", "")
                            attack_type = result_lines[1].replace("Type of attack: ", "")
                            reason = result_lines[2].replace("Reason: ", "")
                            
                            results.append({
                                "success": True,
                                "status": status,
                                "attack_type": attack_type if attack_type != "None" else None,
                                "reason": reason,
                                "raw_result": result,
                                "line_number": i + 1
                            })
                            
                            if status == "Malicious":
                                malicious_count += 1
                        else:
                            results.append({
                                "success": False,
                                "error": "Unexpected result format",
                                "raw_result": result,
                                "line_number": i + 1
                            })
                            error_count += 1
                    else:
                        results.append({
                            "success": False,
                            "error": result.replace("Error: ", ""),
                            "raw_result": result,
                            "line_number": i + 1
                        })
                        error_count += 1
        else:
            # Process CSV more robustly using csv.reader to handle quoting and embedded commas
            # Normalize newlines and strip BOM if present
            content = file_content.replace('\r\n', '\n').replace('\r', '\n')
            if content.startswith('\ufeff'):
                content = content.lstrip('\ufeff')

            reader = csv.reader(io.StringIO(content))
            rows = list(reader)
            # If first row is header, skip it
            start_idx = 1 if has_header and len(rows) > 0 else 0

            for idx, row in enumerate(rows[start_idx:], start=start_idx):
                try:
                    # Reconstruct a normalized CSV line for the classifier using csv.writer
                    out = io.StringIO()
                    writer = csv.writer(out)
                    writer.writerow(row)
                    line_str = out.getvalue().strip('\n')

                    if not line_str.strip():
                        # skip empty lines
                        continue

                    success, result = classifier.process_activity(line_str)
                    if success:
                        result_lines = result.strip().split('\n')
                        if len(result_lines) >= 3:
                            status = result_lines[0].replace("Activity status: ", "")
                            attack_type = result_lines[1].replace("Type of attack: ", "")
                            reason = result_lines[2].replace("Reason: ", "")

                            results.append({
                                "success": True,
                                "status": status,
                                "attack_type": attack_type if attack_type != "None" else None,
                                "reason": reason,
                                "raw_result": result,
                                "line_number": idx + 1
                            })

                            if status == "Malicious":
                                malicious_count += 1
                        else:
                            results.append({
                                "success": False,
                                "error": "Unexpected result format",
                                "raw_result": result,
                                "line_number": idx + 1
                            })
                            error_count += 1
                    else:
                        # Log the problematic line to help debugging
                        app.logger.debug(f"Classifier error for file {filename} line {idx+1}: {line_str}")
                        results.append({
                            "success": False,
                            "error": result.replace("Error: ", ""),
                            "raw_result": result,
                            "line_number": idx + 1
                        })
                        error_count += 1
                except Exception as e:
                    app.logger.exception(f"Failed processing row {idx+1} in {filename}: {e}")
                    results.append({
                        "success": False,
                        "error": f"Processing failed: {str(e)}",
                        "raw_result": "",
                        "line_number": idx + 1
                    })
                    error_count += 1
        
        return {
            "success": True,
            "results": results,
            "total_count": len(results),
            "malicious_count": malicious_count,
            "error_count": error_count
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "results": [],
            "total_count": 0,
            "malicious_count": 0,
            "error_count": 1
        }

def process_batch_files_async(task_id, files_data, has_header):
    """Process multiple files asynchronously."""
    batch_tasks[task_id] = {
        "status": "processing",
        "progress": 0,
        "current_file": "",
        "total_files": len(files_data),
        "processed_files": 0,
        "start_time": datetime.now().isoformat()
    }
    
    all_results = []
    total_malicious = 0
    total_errors = 0
    total_records = 0
    
    try:
        for i, (filename, content) in enumerate(files_data):
            batch_tasks[task_id]["current_file"] = filename
            batch_tasks[task_id]["progress"] = int((i / len(files_data)) * 100)
            
            # Process the file
            file_result = process_single_file(content, filename, has_header)
            
            if file_result["success"]:
                # Add file info to each result
                for result in file_result["results"]:
                    result["filename"] = filename
                    all_results.append(result)
                
                total_malicious += file_result["malicious_count"]
                total_errors += file_result["error_count"]
                total_records += file_result["total_count"]
            
            batch_tasks[task_id]["processed_files"] = i + 1
        
        # Mark as completed
        batch_tasks[task_id]["status"] = "completed"
        batch_tasks[task_id]["progress"] = 100
        batch_tasks[task_id]["end_time"] = datetime.now().isoformat()

        # Normalize results to enforce contract: ensure keys exist and aggregates match
        def _normalize_item(r):
            # Extract from raw_result if needed
            def from_raw(key):
                try:
                    raw = r.get('raw_result') or ''
                    parts = raw.split('\n')
                    if key == 'status' and len(parts) > 0:
                        return parts[0].replace('Activity status: ', '').strip()
                    if key == 'attack_type' and len(parts) > 1:
                        val = parts[1].replace('Type of attack: ', '').strip()
                        return None if val == 'None' else val
                    if key == 'reason' and len(parts) > 2:
                        return parts[2].replace('Reason: ', '').strip()
                except Exception:
                    return ''
                return ''

            # Determine success explicitly (some entries use 'success': False and 'error')
            success_flag = bool(r.get('success', True))

            # If this result represents an error, normalize to a clear error shape
            if not success_flag:
                # Prefer explicit error field, else try to extract from raw_result
                err_msg = r.get('error') or ''
                if not err_msg:
                    raw = (r.get('raw_result') or '').strip()
                    # raw may be like 'Error: ...' or a single-line message
                    if raw.lower().startswith('error:'):
                        err_msg = raw.split(':', 1)[1].strip()
                    else:
                        err_msg = raw

                return {
                    'status': 'Error',
                    'attack_type': None,
                    'reason': err_msg or 'Processing error',
                    'filename': r.get('filename') or 'unknown',
                    'line_number': r.get('line_number') or r.get('line') or None,
                    'success': False,
                    'raw_result': r.get('raw_result', '')
                }

            # Normal (successful) result path
            status = r.get('status') or r.get('Status') or from_raw('status') or 'Unknown'
            attack_type = r.get('attack_type') if ('attack_type' in r) else (r.get('Type of attack') or from_raw('attack_type'))
            if attack_type == 'None':
                attack_type = None
            reason = r.get('reason') or r.get('Reason') or from_raw('reason') or ''

            return {
                'status': status,
                'attack_type': attack_type,
                'reason': reason,
                'filename': r.get('filename') or 'unknown',
                'line_number': r.get('line_number') or r.get('line') or None,
                'success': True,
                'raw_result': r.get('raw_result', '')
            }

        normalized = [_normalize_item(it) for it in all_results]
        # Recompute aggregates from normalized list (source of truth)
        total_records = len(normalized)
        total_malicious = sum(1 for it in normalized if it['success'] and (it['status'] or '').lower() == 'malicious')
        total_errors = sum(1 for it in normalized if not it['success'])

        # Store results
        batch_results[task_id] = {
            "success": True,
            "results": normalized,
            "total_count": total_records,
            "malicious_count": total_malicious,
            "error_count": total_errors,
            "files_processed": len(files_data),
            "processing_time": batch_tasks[task_id]["end_time"]
        }
        # Persist a summary to disk (append as JSON Lines)
        try:
            log_entry = {
                'task_id': task_id,
                'files_processed': len(files_data),
                'total_count': total_records,
                'malicious_count': total_malicious,
                'error_count': total_errors,
                'start_time': batch_tasks[task_id].get('start_time'),
                'end_time': batch_tasks[task_id].get('end_time')
            }
            log_path = os.path.join(os.getcwd(), 'batch_logs.jsonl')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            batch_tasks[task_id]['log_error'] = str(e)
        # Also persist to a small SQLite DB for reliability
        try:
            db_path = os.path.join(os.getcwd(), 'batch_logs.db')
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS batch_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    files_processed INTEGER,
                    total_count INTEGER,
                    malicious_count INTEGER,
                    error_count INTEGER,
                    start_time TEXT,
                    end_time TEXT
                )
            ''')
            cur.execute(
                'INSERT INTO batch_summaries (task_id, files_processed, total_count, malicious_count, error_count, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (log_entry['task_id'], log_entry['files_processed'], log_entry['total_count'], log_entry['malicious_count'], log_entry['error_count'], log_entry['start_time'], log_entry['end_time'])
            )
            conn.commit()
            conn.close()
        except Exception as e:
            batch_tasks[task_id]['db_log_error'] = str(e)
        
    except Exception as e:
        batch_tasks[task_id]["status"] = "error"
        batch_tasks[task_id]["error"] = str(e)
        batch_results[task_id] = {
            "success": False,
            "error": str(e)
        }

@app.route('/api/classify/batch', methods=['POST'])
def classify_batch():
    """
    Start batch processing for multiple files.
    
    Expected form data:
    - files: Multiple CSV or JSON files
    - has_header: boolean (for CSV files)
    
    Returns:
    {
        "success": true/false,
        "task_id": "unique_task_id",
        "message": "Processing started"
    }
    """
    try:
        files = request.files.getlist('files')
        has_header = request.form.get('has_header', 'false').lower() == 'true'
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                "success": False,
                "error": "No files provided"
            }), 400
        
        # Generate unique task ID
        task_id = f"batch_{int(time.time() * 1000)}"
        
        # Prepare files data
        files_data = []
        for file in files:
            if file.filename:
                raw = file.read()
                try:
                    content = raw.decode('utf-8')
                except Exception:
                    # fallback with latin-1 to avoid decode errors
                    content = raw.decode('latin-1')
                files_data.append((file.filename, content))
                # Log file receipt for debugging
                try:
                    sample = content[:200].replace('\n', '\\n')
                    app.logger.debug(f"Received upload: {file.filename} size={len(raw)} sample='{sample}'")
                except Exception:
                    app.logger.debug(f"Received upload: {file.filename} size={len(raw)} (sample unavailable)")
        
        if not files_data:
            return jsonify({
                "success": False,
                "error": "No valid files to process"
            }), 400
        
        # Start async processing
        thread = threading.Thread(
            target=process_batch_files_async,
            args=(task_id, files_data, has_header)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "task_id": task_id,
            "message": f"Processing started for {len(files_data)} files",
            "total_files": len(files_data)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to start processing: {str(e)}"
        }), 500

@app.route('/api/batch/status/<task_id>', methods=['GET'])
def get_batch_status(task_id):
    """Get the status of a batch processing task."""
    if task_id not in batch_tasks:
        return jsonify({
            "success": False,
            "error": "Task not found"
        }), 404
    
    task_info = batch_tasks[task_id].copy()
    return jsonify({
        "success": True,
        "task": task_info
    })

@app.route('/api/batch/results/<task_id>', methods=['GET'])
def get_batch_results(task_id):
    """Get the results of a completed batch processing task."""
    if task_id not in batch_results:
        return jsonify({
            "success": False,
            "error": "Results not found"
        }), 404
    
    return jsonify(batch_results[task_id])

@app.route('/api/sample-data', methods=['GET'])
def get_sample_data():
    """Get sample data for testing."""
    sample_csv = '2024-07-31T00:00:00,177.52.183.80,192.168.1.50,HTTPS,blocked,suspicious,ids,45164,"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",/login?backup.sql'
    sample_json = '{"timestamp": "2024-04-07T00:00:00", "source_ip": "192.168.1.248", "dest_ip": "192.168.1.15", "protocol": "HTTP", "action": "allowed", "threat_label": "benign", "log_type": "application", "bytes_transferred": "20652", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "request_path": "/login"}'
    
    return jsonify({
        "sample_csv": sample_csv,
        "sample_json": sample_json
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)


