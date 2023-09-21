from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired

class CSVForm(FlaskForm):
	csv = FileField('Impor CSV Organisasi', validators=[DataRequired(), FileAllowed(['csv'])])
	
	submit = SubmitField('proses')