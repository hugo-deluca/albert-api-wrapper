from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Main dashboard showing overview."""
    try:
        albert = current_app.albert
        health = albert.get_health()
        collections = albert.get_collections()
        models = albert.get_models()
        
        return render_template('dashboard.html', 
                             health=health, 
                             collections_count=len(collections),
                             models_count=len(models))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', health={'status': 'error'})

# ========== COLLECTIONS ==========

@main_bp.route('/collections')
def collections():
    """List all collections."""
    try:
        albert = current_app.albert
        collections_list = albert.get_collections()
        return render_template('collections.html', collections=collections_list)
    except Exception as e:
        flash(f'Error loading collections: {str(e)}', 'error')
        return render_template('collections.html', collections=[])

@main_bp.route('/api/collections', methods=['GET'])
def api_get_collections():
    """API endpoint to get collections."""
    try:
        albert = current_app.albert
        collections = albert.get_collections()
        return jsonify({'success': True, 'data': collections})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/collections', methods=['POST'])
def api_create_collection():
    """API endpoint to create a collection."""
    try:
        data = request.get_json()
        albert = current_app.albert
        result = albert.create_collection(
            name=data.get('name'),
            description=data.get('description', '')
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/collections/<int:collection_id>', methods=['DELETE'])
def api_delete_collection(collection_id):
    """API endpoint to delete a collection."""
    try:
        albert = current_app.albert
        albert.delete_collection(collection_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== DOCUMENTS ==========

@main_bp.route('/documents')
def documents():
    """List all documents with pagination."""
    collection_id = request.args.get('collection', type=int, default=0)
    page = request.args.get('page', type=int, default=1)
    limit = request.args.get('limit', type=int, default=20)
    name = request.args.get('name', type=str, default=None)
    
    # Calculate offset from page number
    offset = (page - 1) * limit
    
    try:
        albert = current_app.albert
        documents_list = albert.get_documents(
            name=name,
            collection=collection_id,
            limit=limit,
            offset=offset
        )
        collections_list = albert.get_collections()
        
        # Check if there are more documents (for next page button)
        has_more = len(documents_list) == limit
        
        return render_template('documents.html', 
                             documents=documents_list, 
                             collections=collections_list,
                             selected_collection=collection_id,
                             current_page=page,
                             limit=limit,
                             has_more=has_more)
    except Exception as e:
        flash(f'Error loading documents: {str(e)}', 'error')
        return render_template('documents.html', 
                             documents=[], 
                             collections=[],
                             current_page=1,
                             limit=limit,
                             has_more=False)

@main_bp.route('/api/documents', methods=['GET'])
def api_get_documents():
    """API endpoint to get documents with pagination."""
    collection_id = request.args.get('collection', type=int, default=0)
    limit = request.args.get('limit', type=int, default=20)
    offset = request.args.get('offset', type=int, default=0)
    name = request.args.get('name', type=str, default=None)
    
    try:
        albert = current_app.albert
        documents = albert.get_documents(
            name=name,
            collection=collection_id,
            limit=limit,
            offset=offset
        )
        return jsonify({
            'success': True, 
            'data': documents,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/documents', methods=['POST'])
def api_upload_document():
    """API endpoint to upload a document."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        collection_id = request.form.get('collection_id', type=int)
        
        if not collection_id:
            return jsonify({'success': False, 'error': 'Collection ID required'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        
        # Upload directly using file object (no temp file needed!)
        albert = current_app.albert
        result = albert.create_document(
            file_name=filename,
            file_obj=file.stream,
            collection_id=collection_id
        )
        
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/documents/<int:document_id>', methods=['DELETE'])
def api_delete_document(document_id):
    """API endpoint to delete a document."""
    try:
        albert = current_app.albert
        albert.delete_document(document_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== CHAT ==========

@main_bp.route('/chat')
def chat():
    """Chat interface."""
    try:
        albert = current_app.albert
        collections_list = albert.get_collections()
        
        # Get models safely
        try:
            models = albert.get_models()
        except Exception as e:
            print(f"Error fetching models: {e}")
            # Fallback to default models if API call fails
            models = [
                {'id': 'albert-small', 'name': 'Albert Small'},
                {'id': 'albert-large', 'name': 'Albert Large'}
            ]
        
        return render_template('chat.html', collections=collections_list, models=models)
    except Exception as e:
        flash(f'Error loading chat: {str(e)}', 'error')
        # Return with empty data
        return render_template('chat.html', collections=[], models=[
            {'id': 'albert-small', 'name': 'Albert Small'},
            {'id': 'albert-large', 'name': 'Albert Large'}
        ])

@main_bp.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        albert = current_app.albert
        
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
            
        model = data.get('model', 'albert-small')
        collections = data.get('collections', [])
        
        if collections:
            # Chat with search
            response = albert.chat_with_search(
                prompt=prompt,
                collections=collections,
                model=model
            )
        else:
            # Simple chat
            response = albert.chat(prompt=prompt, model=model)
        
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Chat error: {error_details}")  # Log to console
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for search."""
    try:
        data = request.get_json()
        albert = current_app.albert
        
        results = albert.search(
            prompt=data.get('prompt'),
            collections=data.get('collections', [])
        )
        
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500