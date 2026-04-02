"""
Monitoring manager for Flask Admin Pro.
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from ..models import RequestLog


class MonitorManager:
    """Handle monitoring and statistics."""
    
    def __init__(self, db=None):
        self.db = db
    
    def log_request(self, method, path, status_code, response_time, ip_address):
        if not self.db:
            return
        
        log = RequestLog(
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
            ip_address=ip_address,
        )
        self.db.session.add(log)
        self.db.session.commit()
    
    def get_stats(self, range_hours=24):
        if not self.db:
            return {}
        
        since = datetime.utcnow() - timedelta(hours=range_hours)
        
        total_requests = RequestLog.query.filter(RequestLog.created_at >= since).count()
        error_requests = RequestLog.query.filter(
            RequestLog.created_at >= since,
            RequestLog.status_code >= 400
        ).count()
        
        avg_response = self.db.session.query(
            func.avg(RequestLog.response_time)
        ).filter(RequestLog.created_at >= since).scalar() or 0
        
        hourly_stats = self.db.session.query(
            func.strftime('%Y-%m-%d %H:00', RequestLog.created_at).label('hour'),
            func.count(RequestLog.id).label('count')
        ).filter(
            RequestLog.created_at >= since
        ).group_by('hour').all()
        
        requests_by_hour = [
            {'hour': row.hour, 'count': row.count}
            for row in hourly_stats
        ]
        
        return {
            'total_requests': total_requests,
            'error_requests': error_requests,
            'error_rate': round(error_requests / total_requests * 100, 2) if total_requests > 0 else 0,
            'avg_response_time': round(avg_response, 2),
            'requests_by_hour': requests_by_hour,
            'range_hours': range_hours,
        }
    
    def get_logs(self, page=1, per_page=50, method=None, status_min=None):
        query = RequestLog.query
        
        if method:
            query = query.filter(RequestLog.method == method)
        
        if status_min:
            query = query.filter(RequestLog.status_code >= status_min)
        
        query = query.order_by(RequestLog.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logs = [log.to_dict() for log in pagination.items]
        
        return {
            'logs': logs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        }
