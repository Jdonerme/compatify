from flask_wtf import Form
from wtforms.fields import SelectMultipleField
from wtforms.validators import DataRequired

class SelectForm(Form):
	response = SelectMultipleField('Response', choices = [], \
									  validators=[DataRequired()])