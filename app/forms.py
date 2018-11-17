from flask_wtf import FlaskForm
from wtforms.fields import SelectMultipleField
from wtforms.validators import DataRequired

class SelectForm(FlaskForm):
	response = SelectMultipleField('Response', choices = [], \
									  validators=[DataRequired()])