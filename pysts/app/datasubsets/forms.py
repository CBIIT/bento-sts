from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired, Optional
from wtforms_components import SelectField

class ChooseSubsetForm(FlaskForm):
    datasubsets = SelectField("Data Subset ", choices=[
        ('ICDC', 'ICDC'), ('CTDC', 'CTDC')
    ])
    submit = SubmitField("Select Data Subset")

class gammaSubsetForm(FlaskForm):
    datasubsets = SelectField("Data Subset ", )
    submit = SubmitField("Select Data Subset")

class deltaOneForm(FlaskForm):
    aset = SelectField("Data Subset ", )
    bset = SelectField("Data Subset ", )
    newsubset_model = SelectField("Model for New Subset ", )
    newsubset_tag = StringField('Name of New Subset', [Optional()])
    submit = SubmitField("Submit")
    create = SubmitField("Create")
