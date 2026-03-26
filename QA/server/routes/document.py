"""
Document routes
Provides document upload, list, and delete endpoints
"""
import os
import uuid
from flask import Blueprint, request, g, current_app
from models import db
from models.document import Document
from models.knowledge_base import KnowledgeBase
from utils.auth import login_required, admin_required
from utils.response import success, error, page_response

# Create document blueprint
doc_bp = Blueprint('document', __name__)


def allowed_file(filename):
    """Check whether file extension is allowed for upload"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@doc_bp.route('/list', methods=['GET'])
@login_required
def get_list():
    """
    Get document list (paginated)
    Query params: page, page_size, kb_id
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    kb_id = request.args.get('kb_id', type=int)

    query = Document.query
    if kb_id:
        query = query.filter_by(kb_id=kb_id)

    query = query.order_by(Document.create_time.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    items = [item.to_dict() for item in pagination.items]
    return page_response(items, pagination.total, page, page_size)


@doc_bp.route('/upload', methods=['POST'])
@admin_required
def upload():
    """
    Upload document and run vectorization (admin only)
    Form params: file, kb_id
    """
    if 'file' not in request.files:
        return error('Please select a file to upload')

    file = request.files['file']
    kb_id = request.form.get('kb_id', type=int)

    if not kb_id:
        return error('Please select a knowledge base')

    if file.filename == '':
        return error('Please select a file to upload')

    if not allowed_file(file.filename):
        return error(f"Unsupported file type. Supported types: {', '.join(current_app.config['ALLOWED_EXTENSIONS'])}")

    # Validate knowledge base exists
    kb = KnowledgeBase.query.get(kb_id)
    if not kb:
        return error('Knowledge base does not exist')

    # Generate unique filename and save
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
    file.save(file_path)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Create document record
    doc = Document(
        kb_id=kb_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_ext,
        creator_id=g.user_id
    )
    db.session.add(doc)
    db.session.commit()

    # Run document vectorization
    try:
        from services.vector_service import VectorService, OllamaServiceError
        vector_service = VectorService()
        chunk_count = vector_service.process_document(doc.id, file_path, file_ext, kb_id)

        # Update document status
        doc.status = 'vectorized'
        doc.chunk_count = chunk_count

        # Update knowledge base document count
        kb.doc_count = Document.query.filter_by(kb_id=kb_id, status='vectorized').count()
        db.session.commit()
    except OllamaServiceError as e:
        doc.status = 'failed'
        db.session.commit()
        return error(f'Vector service error: {str(e)}')
    except ConnectionError:
        doc.status = 'failed'
        db.session.commit()
        return error('Unable to connect to Ollama service. Please ensure Ollama is running and accessible')
    except Exception as e:
        doc.status = 'failed'
        db.session.commit()
        err_msg = str(e)
        if 'status code' in err_msg:
            return error(f'Ollama service processing error. Please check Ollama status and system resources: {err_msg}')
        return error(f'Document vectorization failed: {err_msg}')

    return success(doc.to_dict(), '上传成功')


@doc_bp.route('/<int:doc_id>', methods=['DELETE'])
@admin_required
def delete(doc_id):
    """
    Delete document (admin only)
    Also delete related vectors and physical file
    """
    doc = Document.query.get(doc_id)
    if not doc:
        return error('Document does not exist', 404)

    kb_id = doc.kb_id

    # Delete vector data
    try:
        from services.vector_service import VectorService
        vector_service = VectorService()
        vector_service.delete_document(doc.id, kb_id)
    except Exception:
        pass

    # Delete physical file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete database record
    db.session.delete(doc)

    # Update knowledge base document count
    kb = KnowledgeBase.query.get(kb_id)
    if kb:
        kb.doc_count = Document.query.filter_by(kb_id=kb_id, status='vectorized').count() - 1
        if kb.doc_count < 0:
            kb.doc_count = 0

    db.session.commit()
    return success(message='Deleted successfully')

