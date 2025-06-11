import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # For weather API
    API_SPACES_API_KEY = os.environ.get('API_SPACES_API_KEY') or 'jt9waq8f5rmk0jd0jon5s9rtshsjydqr'
    
    # For Alibaba Bailian/Tongyi Qianwen LLM
    BAILIAN_API_KEY = os.environ.get('BAILIAN_API_KEY')
    
    # 支持中文字体
    FONT_PATH = "c:/Windows/Fonts/simsun.ttc" 