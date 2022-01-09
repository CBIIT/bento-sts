from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired

class SearchForm(FlaskForm):
    qstring = StringField("Query", validators=[DataRequired()])
    terms = SubmitField('Search Terms')
    models = SubmitField('Search Models')
    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)

class SelectModelForm(FlaskForm):
    model = SelectField('Model')
    filter = SubmitField('Filter')
    export = SubmitField('Export JSON')




        
