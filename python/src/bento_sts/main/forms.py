from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    qstring = StringField("Query", validators=[DataRequired()])
    terms = SubmitField("Search Terms")
    models = SubmitField("Search Models")

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class SelectModelForm(FlaskForm):
    model = SelectField("Model")
    version = SelectField("Version")
    filter = SubmitField("Filter")
    export = SubmitField("Export JSON")


class SelectVersionForm(FlaskForm):
    version = SelectField('Version')
    submit_version = SubmitField('Version')
    



        
