"""
Statistics routes
Provides dashboard statistics endpoints for admins
"""
from flask import Blueprint
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db
from models.user import User
from models.knowledge_base import KnowledgeBase
from models.document import Document
from models.chat_history import ChatHistory
from utils.auth import admin_required
from utils.response import success

# Create stats blueprint
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/overview', methods=['GET'])
@admin_required
def overview():
    """
    Get dashboard overview statistics (admin only)
    Returns: users, knowledge bases, documents, today questions, 7-day trend, KB document ratio
    """
    # Basic counts
    user_count = User.query.filter_by(status=1).count()
    kb_count = KnowledgeBase.query.filter_by(status=1).count()
    doc_count = Document.query.filter_by(status='vectorized').count()

    # Today question count
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_chat_count = ChatHistory.query.filter(ChatHistory.create_time >= today_start).count()

    # Daily question trend for the last 7 days
    trend_data = []
    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = ChatHistory.query.filter(
            ChatHistory.create_time >= day_start,
            ChatHistory.create_time < day_end
        ).count()
        trend_data.append({
            'date': day_start.strftime('%m-%d'),
            'count': count
        })

    # Document count ratio by knowledge base
    kb_doc_stats = db.session.query(
        KnowledgeBase.kb_name,
        KnowledgeBase.doc_count
    ).filter(
        KnowledgeBase.status == 1,
        KnowledgeBase.doc_count > 0
    ).all()

    kb_doc_data = [{'name': name, 'value': count} for name, count in kb_doc_stats]

    return success({
        'user_count': user_count,
        'kb_count': kb_count,
        'doc_count': doc_count,
        'today_chat_count': today_chat_count,
        'trend_data': trend_data,
        'kb_doc_data': kb_doc_data
    })

