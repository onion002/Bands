"""
统计数据API
提供管理员仪表板所需的统计信息
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from auth_decorators import require_admin, get_current_user
from models import db, Band, Member, Event
import logging

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/dashboard', methods=['GET'])
@require_admin
def get_dashboard_stats():
    """获取管理员仪表板统计数据"""
    try:
        current_user = get_current_user()
        logging.info(f"获取用户 {current_user.username} 的仪表板统计数据")

        # 获取当前管理员的乐队数量（排除软删除）
        bands_count = Band.query.filter_by(owner_id=current_user.id, is_deleted=False).count()
        logging.info(f"乐队数量: {bands_count}")

        # 获取当前管理员所有乐队的成员总数（排除软删除）
        band_ids = [band.id for band in Band.query.filter_by(owner_id=current_user.id, is_deleted=False).all()]
        members_count = 0
        if band_ids:
            members_count = Member.query.filter(
                Member.band_id.in_(band_ids),
                Member.is_deleted == False
            ).count()
        logging.info(f"成员数量: {members_count}")

        # 获取当前管理员的活动数量（排除软删除）
        events_count = Event.query.filter_by(owner_id=current_user.id, is_deleted=False).count()
        logging.info(f"活动数量: {events_count}")

        # 获取进行中的活动数量（今天及以后的活动，排除软删除）
        today = datetime.now().date()
        active_events_count = Event.query.filter(
            Event.owner_id == current_user.id,
            Event.event_date >= today,
            Event.is_deleted == False
        ).count()
        logging.info(f"进行中活动数量: {active_events_count}")

        result = {
            'bands': bands_count,
            'members': members_count,
            'events': events_count,
            'activeEvents': active_events_count
        }
        logging.info(f"返回统计数据: {result}")

        return jsonify(result)

    except Exception as e:
        logging.error(f"获取仪表板统计数据失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取统计数据失败'}), 500

@stats_bp.route('/recent-activities', methods=['GET'])
@require_admin
def get_recent_activities():
    """获取最近活动记录"""
    try:
        current_user = get_current_user()
        activities = []
        
        # 获取最近创建的乐队（最近7天，排除软删除）
        recent_date = datetime.now() - timedelta(days=7)
        recent_bands = Band.query.filter(
            Band.owner_id == current_user.id,
            Band.created_at >= recent_date,
            Band.is_deleted == False
        ).order_by(Band.created_at.desc()).limit(3).all()

        for band in recent_bands:
            activities.append({
                'id': f'band_{band.id}',
                'icon': 'fas fa-music',
                'text': f'创建了新乐队 "{band.name}"',
                'time': format_time_ago(band.created_at),
                'timestamp': band.created_at.isoformat()
            })

        # 获取最近创建的成员（最近7天，排除软删除）
        band_ids = [band.id for band in Band.query.filter_by(owner_id=current_user.id, is_deleted=False).all()]
        if band_ids:
            recent_members = Member.query.filter(
                Member.band_id.in_(band_ids),
                Member.created_at >= recent_date,
                Member.is_deleted == False
            ).order_by(Member.created_at.desc()).limit(3).all()

            for member in recent_members:
                activities.append({
                    'id': f'member_{member.id}',
                    'icon': 'fas fa-user-plus',
                    'text': f'添加了新成员 "{member.name}"',
                    'time': format_time_ago(member.created_at),
                    'timestamp': member.created_at.isoformat()
                })

        # 获取最近创建的活动（最近7天，排除软删除）
        recent_events = Event.query.filter(
            Event.owner_id == current_user.id,
            Event.created_at >= recent_date,
            Event.is_deleted == False
        ).order_by(Event.created_at.desc()).limit(3).all()
        
        for event in recent_events:
            activities.append({
                'id': f'event_{event.id}',
                'icon': 'fas fa-calendar-plus',
                'text': f'创建了新活动 "{event.title}"',
                'time': format_time_ago(event.created_at),
                'timestamp': event.created_at.isoformat()
            })
        
        # 按时间排序，最新的在前面
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 只返回最近的5个活动
        return jsonify(activities[:5])
        
    except Exception as e:
        logging.error(f"获取最近活动失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取最近活动失败'}), 500

def format_time_ago(timestamp):
    """格式化时间为相对时间"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f'{diff.days}天前'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours}小时前'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes}分钟前'
    else:
        return '刚刚'
