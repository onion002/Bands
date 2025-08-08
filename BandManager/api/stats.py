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

        # 计算一周前的日期
        one_week_ago = datetime.now() - timedelta(days=7)

        # 获取当前管理员的乐队数量（排除软删除）
        bands_count = Band.query.filter_by(owner_id=current_user.id, is_deleted=False).count()
        # 获取一周前的乐队数量
        bands_count_week_ago = Band.query.filter(
            Band.owner_id == current_user.id,
            Band.is_deleted == False,
            Band.created_at <= one_week_ago
        ).count()
        # 计算乐队数量变化
        bands_change = bands_count - bands_count_week_ago
        logging.info(f"乐队数量: {bands_count}, 一周前: {bands_count_week_ago}, 变化: {bands_change}")

        # 获取当前管理员所有乐队的成员总数（排除软删除）
        band_ids = [band.id for band in Band.query.filter_by(owner_id=current_user.id, is_deleted=False).all()]
        members_count = 0
        members_count_week_ago = 0
        if band_ids:
            members_count = Member.query.filter(
                Member.band_id.in_(band_ids),
                Member.is_deleted == False
            ).count()
            # 获取一周前的成员数量
            members_count_week_ago = Member.query.filter(
                Member.band_id.in_(band_ids),
                Member.is_deleted == False,
                Member.created_at <= one_week_ago
            ).count()
        # 计算成员数量变化
        members_change = members_count - members_count_week_ago
        logging.info(f"成员数量: {members_count}, 一周前: {members_count_week_ago}, 变化: {members_change}")

        # 获取当前管理员的活动数量（排除软删除）
        events_count = Event.query.filter_by(owner_id=current_user.id, is_deleted=False).count()
        # 获取一周前的活动数量
        events_count_week_ago = Event.query.filter(
            Event.owner_id == current_user.id,
            Event.is_deleted == False,
            Event.created_at <= one_week_ago
        ).count()
        # 计算活动数量变化
        events_change = events_count - events_count_week_ago
        logging.info(f"活动数量: {events_count}, 一周前: {events_count_week_ago}, 变化: {events_change}")

        # 获取进行中的活动数量（今天及以后的活动，排除软删除）
        today = datetime.now().date()
        active_events_count = Event.query.filter(
            Event.owner_id == current_user.id,
            Event.event_date >= today,
            Event.is_deleted == False
        ).count()
        logging.info(f"进行中活动数量: {active_events_count}")

        result = {
            'bands': {
                'count': bands_count,
                'change': bands_change
            },
            'members': {
                'count': members_count,
                'change': members_change
            },
            'events': {
                'count': events_count,
                'change': events_change
            },
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
    # 确保timestamp是datetime对象
    if not isinstance(timestamp, datetime):
        timestamp = datetime.fromisoformat(timestamp)
    
    # 转换为UTC时区进行比较，避免本地时区差异
    timestamp_utc = timestamp.astimezone(tz=None) if timestamp.tzinfo else timestamp
    now_utc = datetime.utcnow()
    
    diff = now_utc - timestamp_utc
    total_seconds = diff.total_seconds()
    
    # 添加详细日志以诊断问题
    logging.info(f"format_time_ago - original timestamp: {timestamp}")
    logging.info(f"format_time_ago - timestamp_utc: {timestamp_utc}, now_utc: {now_utc}")
    logging.info(f"format_time_ago - diff: {diff}, total_seconds: {total_seconds}")
    
    if total_seconds >= 86400:  # 24小时 = 86400秒
        days = int(total_seconds // 86400)
        return f'{days}天前'
    elif total_seconds >= 3600:  # 1小时 = 3600秒
        hours = int(total_seconds // 3600)
        return f'{hours}小时前'
    elif total_seconds >= 60:  # 1分钟 = 60秒
        minutes = int(total_seconds // 60)
        return f'{minutes}分钟前'
    else:
        return '刚刚'

# 添加一个简单的测试函数
def test_format_time_ago():
    """测试format_time_ago函数"""
    # 测试刚刚
    now = datetime.utcnow()
    print(f"刚刚: {format_time_ago(now)}")
    
    # 测试1分钟前
    one_minute_ago = now - timedelta(minutes=1)
    print(f"1分钟前: {format_time_ago(one_minute_ago)}")
    
    # 测试1小时前
    one_hour_ago = now - timedelta(hours=1)
    print(f"1小时前: {format_time_ago(one_hour_ago)}")
    
    # 测试1天前
    one_day_ago = now - timedelta(days=1)
    print(f"1天前: {format_time_ago(one_day_ago)}")
