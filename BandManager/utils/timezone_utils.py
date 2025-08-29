"""
时区工具模块 - 处理东8区时间转换
"""
from datetime import datetime, timezone, timedelta
import pytz

# 东8区时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def get_beijing_time():
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)

def utc_to_beijing(utc_datetime):
    """将UTC时间转换为北京时间"""
    if utc_datetime is None:
        return None
    
    # 如果是naive datetime，假设它是UTC时间
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
    
    # 转换为北京时间
    return utc_datetime.astimezone(BEIJING_TZ)

def beijing_to_utc(beijing_datetime):
    """将北京时间转换为UTC时间"""
    if beijing_datetime is None:
        return None
    
    # 如果是naive datetime，假设它是北京时间
    if beijing_datetime.tzinfo is None:
        beijing_datetime = BEIJING_TZ.localize(beijing_datetime)
    
    # 转换为UTC时间
    return beijing_datetime.astimezone(pytz.UTC)

def format_beijing_time(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """格式化北京时间"""
    if dt is None:
        return None
    
    beijing_time = utc_to_beijing(dt)
    return beijing_time.strftime(format_str)

def get_beijing_now_for_db():
    """获取用于数据库存储的北京时间（转换为UTC）"""
    beijing_now = get_beijing_time()
    return beijing_to_utc(beijing_now).replace(tzinfo=None)
