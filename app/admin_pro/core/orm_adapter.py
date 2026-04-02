"""
ORM adapter for Flask Admin Pro.
"""

from datetime import datetime


class ORMAdapter:
    """Adapter for ORM operations."""
    
    def __init__(self, db=None):
        self.db = db
    
    def get_models(self):
        if self.db is None:
            return []
        return list(self.db.Model._decl_class_registry.values())
    
    def get_model_by_name(self, name):
        models = self.get_models()
        for model in models:
            if hasattr(model, '__name__') and model.__name__ == name:
                if name.startswith('_'):
                    continue
                return model
        return None
    
    def get_model_info(self, model):
        if not model or not hasattr(model, '__table__'):
            return None
        
        columns = []
        for col in model.__table__.columns:
            col_info = {
                'name': col.name,
                'type': self._get_column_type(col.type),
                'nullable': col.nullable,
                'primary_key': col.primary_key,
                'is_datetime': 'datetime' in str(col.type).lower(),
                'is_integer': 'int' in str(col.type).lower(),
                'is_string': 'string' in str(col.type).lower() or 'text' in str(col.type).lower(),
            }
            columns.append(col_info)
        
        return {
            'name': model.__name__,
            'table': model.__tablename__,
            'columns': columns,
        }
    
    def _get_column_type(self, col_type):
        type_str = str(col_type).lower()
        if 'int' in type_str:
            return 'integer'
        elif 'string' in type_str or 'text' in type_str or 'char' in type_str:
            return 'string'
        elif 'datetime' in type_str or 'timestamp' in type_str:
            return 'datetime'
        elif 'float' in type_str or 'decimal' in type_str:
            return 'number'
        elif 'bool' in type_str:
            return 'boolean'
        else:
            return 'string'
