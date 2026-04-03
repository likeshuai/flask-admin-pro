"""
ORM adapter for Flask Admin Pro.
"""

from datetime import datetime


class ORMAdapter:
    """Adapter for ORM operations."""
    
    def __init__(self, db=None):
        self.db = db
        self._models_cache = []
    
    def register_model(self, model):
        """手动注册一个模型"""
        if model not in self._models_cache:
            self._models_cache.append(model)
    
    def get_models(self):
        """获取所有注册的SQLAlchemy模型"""
        if self.db is None:
            return self._models_cache
        
        models = list(self._models_cache)
        
        try:
            # 方法1: SQLAlchemy 2.x / Flask-SQLAlchemy 3.x - 使用 registry.mappers
            if hasattr(self.db.Model, 'registry') and hasattr(self.db.Model.registry, 'mappers'):
                for mapper in self.db.Model.registry.mappers:
                    model_class = mapper.class_
                    if self._is_valid_model(model_class) and model_class not in models:
                        models.append(model_class)
                if models:
                    return models
        except Exception as e:
            print(f"[ORMAdapter] Error getting models via registry.mappers: {e}")
        
        try:
            # 方法2: 通过 metadata.tables 获取所有表,然后找到对应的模型类
            if hasattr(self.db, 'metadata') and hasattr(self.db.metadata, 'tables'):
                # 获取所有已注册的mapper
                if hasattr(self.db.Model, 'registry') and hasattr(self.db.Model.registry, 'mappers'):
                    for mapper in self.db.Model.registry.mappers:
                        model_class = mapper.class_
                        if self._is_valid_model(model_class) and model_class not in models:
                            models.append(model_class)
        except Exception as e:
            print(f"[ORMAdapter] Error getting models via metadata: {e}")
        
        return models
    
    def _is_valid_model(self, model_class):
        """检查是否是有效的模型类"""
        try:
            return (
                hasattr(model_class, '__tablename__') and 
                hasattr(model_class, '__table__') and
                not model_class.__name__.startswith('_') and
                model_class.__name__ not in ['Model', 'Base']
            )
        except:
            return False
    
    def get_model_by_name(self, name):
        models = self.get_models()
        for model in models:
            if hasattr(model, '__name__') and model.__name__ == name:
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
                'is_boolean': 'bool' in str(col.type).lower(),
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
