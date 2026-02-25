"""
Machine Learning Model Loader
Loads pre-trained churn prediction models and encoders.
"""

import joblib
import os


class MLModels:
    """Singleton class to load and manage ML models."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModels, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance
    
    def _load_models(self):
        """Load ML components with error reporting."""
        try:
            models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
            
            self.model = joblib.load(os.path.join(models_dir, 'churn_model.pkl'))
            self.encoder = joblib.load(os.path.join(models_dir, 'label_encoder.pkl'))
            self.feature_cols = joblib.load(os.path.join(models_dir, 'feature_cols.pkl'))
            
            print("✅ ML Models and Feature list loaded successfully.")
            print(f"📋 Required Features: {self.feature_cols}")
            
        except Exception as e:
            print(f"❌ ERROR: Could not load models. Check if the 'models' folder exists. {e}")
            self.model = None
            self.encoder = None
            self.feature_cols = None
    
    def is_loaded(self):
        """Check if all models are loaded successfully."""
        return all([self.model is not None, self.encoder is not None, self.feature_cols is not None])
    
    def get_model(self):
        """Get the churn prediction model."""
        return self.model
    
    def get_encoder(self):
        """Get the label encoder."""
        return self.encoder
    
    def get_feature_columns(self):
        """Get the list of feature columns."""
        return self.feature_cols


# Create singleton instance
ml_models = MLModels()
