from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Please use a different username.")



class EditPropForm(FlaskForm):
    prophandle = StringField('Handle', validators=[InputRequired(message="cannot be blank"), Length(min=0, max=140, message="length of property handle must be greater than 0 and less than 140 characters")])
    submit = SubmitField("Save Changes")


class DeprecatePropForm(FlaskForm):
    submit = SubmitField("Deprecate Property")


class EditTermForm(FlaskForm):
    termvalue = StringField('Value', validators=[InputRequired(message="cannot be blank"), Length(min=0, max=140, message="length of term value must be greater than 0 and less than 140 characters")])
    submit = SubmitField("Save Changes")


class DeprecateTermForm(FlaskForm):
    submit = SubmitField("Deprecate Term")


class EditNodeForm(FlaskForm):
    nodeHandle = StringField('Handle', validators=[InputRequired(message="cannot be blank"), Length(min=0, max=140, message="length of handle must be greater than 0 and less than 140 characters")])
    submit = SubmitField("Save Changes")

class DeprecateNodeForm(FlaskForm):
    submit = SubmitField("Deprecate Node")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class DiffForm(FlaskForm):
    mdf_a = SelectField("MDF file A", choices=[])
    mdf_b = SelectField("MDF file B", choices=[])
    submit = SubmitField("Get Diff")

class PostForm(FlaskForm):
    post = TextAreaField("Say something", validators=[DataRequired()])
    submit = SubmitField("Submit")


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)
