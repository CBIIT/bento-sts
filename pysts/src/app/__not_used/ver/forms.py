from flask import request
from flask_wtf import FlaskForm
import wtforms
from wtforms import StringField, SubmitField, TextAreaField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired, Optional
from wtforms_components import SelectField

class ModelVersioningForm(FlaskForm):
    #datasubsets = SelectField("Data Subset ",)
    
    releases = SelectField('Releases', choices=[ ] )

    report_format = SelectField('Report Format', choices=[ ('json', 'json'), ('csv', 'csv') ] )

    submit = SubmitField("Get History")

