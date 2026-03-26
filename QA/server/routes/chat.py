"""
QA conversation routes
Provides RAG QA and chat history endpoints
"""
import uuid
import json
from flask import Blueprint, request, g
from models import db
from models.chat_history import ChatHistory
from models.knowledge_base import KnowledgeBase
from utils.auth import login_required
from utils.response import success, error, page_response

# Create chat blueprint
chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/ask', methods=['POST'])
@login_required
def ask():
    """
    RAG knowledge base QA endpoint
    Request params: question, kb_id, session_id (optional)
    Returns: AI answer and reference sources
    """
    data = request.get_json()
    if not data:
        return error('Please provide question information')

    question = data.get('question', '').strip()
    kb_id = data.get('kb_id')
    session_id = data.get('session_id', str(uuid.uuid4().hex[:16]))

    if not question:
        return error('Question cannot be empty')
    if not kb_id:
        return error('Please select a knowledge base')

    # Validate knowledge base exists
    kb = KnowledgeBase.query.get(kb_id)
    if not kb or kb.status != 1:
        return error('Knowledge base does not exist or is disabled')

    # Call RAG service for QA
    try:
        from services.rag_service import RAGService
        rag_service = RAGService()
        answer, source_docs = rag_service.ask(question, kb_id)
    except Exception as e:
        return error(f'QA service exception: {str(e)}')

    # Save chat history
    chat = ChatHistory(
        user_id=g.user_id,
        kb_id=kb_id,
        session_id=session_id,
        question=question,
        answer=answer,
        source_docs=json.dumps(source_docs, ensure_ascii=False)
    )
    db.session.add(chat)
    db.session.commit()

    return success({
        'answer': answer,
        'source_docs': source_docs,
        'session_id': session_id,
        'chat_id': chat.id
    })


@chat_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """
    Get chat history list (paginated)
    Query params: page, page_size, kb_id (optional)
    Regular users can only view their own records; admins can view all
    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    kb_id = request.args.get('kb_id', type=int)

    query = ChatHistory.query

    # Regular users can only view their own chat history
    if g.role != 'admin':
        query = query.filter_by(user_id=g.user_id)

    if kb_id:
        query = query.filter_by(kb_id=kb_id)

    query = query.order_by(ChatHistory.create_time.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    items = [item.to_dict() for item in pagination.items]
    return page_response(items, pagination.total, page, page_size)


@chat_bp.route('/session/<session_id>', methods=['GET'])
@login_required
def get_session(session_id):
    """
    Get all chat records of a specific session
    Path param: session_id
    """
    query = ChatHistory.query.filter_by(session_id=session_id)

    # Regular users can only view their own chats
    if g.role != 'admin':
        query = query.filter_by(user_id=g.user_id)

    chats = query.order_by(ChatHistory.create_time.asc()).all()
    return success([chat.to_dict() for chat in chats])

