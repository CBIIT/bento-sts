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
    """for selecting and exporting"""
    datasubsets = SelectField("Data Subset ", )
    submit = SubmitField("Select Data Subset")

    exportcsv = SubmitField("Export CSV ")
    exportjson = SubmitField("Export JSON")
    exportyaml = SubmitField("Export Yaml")
    exportxlsx = SubmitField("Export XLXS")



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
    aset = SelectField("Edit Data Subset ", )
    bset = SelectField("Reference Data Subset ", )    
    entire_model = SelectField("Reference Model ", )

    newsubset_model = SelectField("Model for New Data Subset ", )
    newsubset_tag = StringField('Name of New Data Subset', [Optional(strip_whitespace=True)])

    submit = SubmitField("Get Data Subsets")
    entire = SubmitField("Get Model")
    create = SubmitField("Create")
