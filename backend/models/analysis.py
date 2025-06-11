import datetime
from ..extensions import db

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False, default='未命名分析')
    # Link to the conversion task that generated this analysis
    task_id = db.Column(db.Integer, db.ForeignKey('conversion_tasks.id'), nullable=False, index=True)
    
    report_content = db.Column(db.Text, nullable=True) # For storing the text report
    
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationship to charts
    charts = db.relationship('AnalysisChart', backref='result', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<AnalysisResult {self.id}>'

class AnalysisChart(db.Model):
    __tablename__ = 'analysis_charts'

    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.String(36), db.ForeignKey('analysis_results.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    # Store chart image as Base64 encoded string in a Text field for DB compatibility
    chart_data = db.Column(db.Text, nullable=False) 

    def __repr__(self):
        return f'<AnalysisChart {self.title}>' 