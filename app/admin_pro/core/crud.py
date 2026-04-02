"""
CRUD operations manager for Flask Admin Pro.
"""

from sqlalchemy import or_
from datetime import datetime


class CRUDManager:
    """Handle CRUD operations for models."""
    
    def __init__(self, db):
        self.db = db
    
    def get_all(self, model, page=1, per_page=20, search=None, sort_by=None, sort_order='asc'):
        query = model.query
        
        if search:
            search_filters = []
            for col in model.__table__.columns:
                if col.type.python_type == str:
                    search_filters.append(col.ilike(f'%{search}%'))
            if search_filters:
                query = query.filter(or_(*search_filters))
        
        if sort_by and hasattr(model, sort_by):
            col = getattr(model, sort_by)
            if sort_order == 'desc':
                query = query.order_by(col.desc())
            else:
                query = query.order_by(col.asc())
        
        total = query.count()
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        data = [self.model_to_dict(item, model) for item in pagination.items]
        
        return {
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
        }
    
    def get_by_id(self, model, id):
        return model.query.get(id)
    
    def create(self, model, data):
        valid_data = {}
        for col in model.__table__.columns:
            if col.name in data and not col.primary_key:
                value = data[col.name]
                if 'datetime' in str(col.type) and value:
                    try:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        pass
                valid_data[col.name] = value
        
        instance = model(**valid_data)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance
    
    def update(self, instance, data):
        model = type(instance)
        
        for col in model.__table__.columns:
            if col.name in data and not col.primary_key:
                value = data[col.name]
                if 'datetime' in str(col.type) and value:
                    try:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        pass
                setattr(instance, col.name, value)
        
        self.db.session.commit()
        return instance
    
    def delete(self, instance):
        self.db.session.delete(instance)
        self.db.session.commit()
    
    def model_to_dict(self, instance, model):
        if instance is None:
            return None
        
        result = {}
        for col in model.__table__.columns:
            value = getattr(instance, col.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[col.name] = value
        return result
