"""
Monitoring manager for Flask Admin Pro.
"""

from datetime import datetime, timedelta
from sqlalchemy import func


class MonitorManager:
    """Handle monitoring and statistics."""
    
    def __init__(self, db=None, RequestLog=None):
        self.db = db
        self.RequestLog = RequestLog
    
    def log_request(self, method, path, status_code, response_time, ip_address):
        if not self.db or not self.RequestLog:
            return
        
        log = self.RequestLog(
            method=method,
            path=path,
            status_code=status_code,
            response_time=response_time,
            ip_address=ip_address,
        )
        self.db.session.add(log)
        self.db.session.commit()
    
    def get_stats(self, range_hours=24):
        if not self.db or not self.RequestLog:
            return {}
        
        since = datetime.utcnow() - timedelta(hours=range_hours)
        
        total_requests = self.db.session.query(self.RequestLog).filter(self.RequestLog.created_at >= since).count()
        error_requests = self.db.session.query(self.RequestLog).filter(
            self.RequestLog.created_at >= since,
            self.RequestLog.status_code >= 400
        ).count()
        
        avg_response = self.db.session.query(
            func.avg(self.RequestLog.response_time)
        ).filter(self.RequestLog.created_at >= since).scalar() or 0
        
        hourly_stats = self.db.session.query(
            func.strftime('%Y-%m-%d %H:00', self.RequestLog.created_at).label('hour'),
            func.count(self.RequestLog.id).label('count')
        ).filter(
            self.RequestLog.created_at >= since
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
        if not self.RequestLog:
            return {'logs': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
        
        query = self.db.session.query(self.RequestLog)
        
        if method:
            query = query.filter(self.RequestLog.method == method)
        
        if status_min:
            query = query.filter(self.RequestLog.status_code >= status_min)
        
        query = query.order_by(self.RequestLog.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        logs = [log.to_dict() for log in pagination.items]
        
        return {
            'logs': logs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        }
