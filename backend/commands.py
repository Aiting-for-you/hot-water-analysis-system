import click
from flask.cli import with_appcontext
from .extensions import db
from .models.user import User
from .models.dataset import Dataset
# from .models.analysis import AnalysisTask # This model is removed

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.cli.add_command(init_db_command) 