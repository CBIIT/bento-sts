from flask import request
from flask_wtf import FlaskForm
import wtforms
from wtforms import StringField, SubmitField, TextAreaField, FieldList, FormField
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


class deltaTwoForm(FlaskForm):
    #addbtn = SubmitField("Add")

    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

class dataSubSet(FlaskForm):
    #nodelabel = StringField()
    #nodeid = StringField()
    #propertylabel = StringField()
    #propertyid = StringField()
    #addbutton = SubmitField('Add')
    pass

class deltaThreeForm(FlaskForm):
    #addbtn = SubmitField("Add")

    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

class deltaOneForm(FlaskForm):
    aset = SelectField("Data Subset ", )
    bset = SelectField("Data Subset ", )
    newsubset_model = SelectField("Model for New Subset ", )
    newsubset_tag = StringField('Name of New Subset', [Optional(strip_whitespace=True)])
    
    #subformA = FieldList(FormField(deltaTwoForm))
    subformB = wtforms.FormField(dataSubSet)

    subformBsize = None

    submit = SubmitField("Submit")
    create = SubmitField("Create")
    addProp = SubmitField("Add")
