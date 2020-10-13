from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_("Please use a different username."))


class EditTermForm(FlaskForm):
    termvalue = StringField('Value', validators=[InputRequired(message="cannot be blank"), Length(min=0, max=140, message="length of term value must be greater than 0 and less than 140 characters")])
    submit = SubmitField("Save Changes")


class DeprecateTermForm(FlaskForm):
    submit = SubmitField("Deprecate Term")


class DiffForm(FlaskForm):
    mdf_a = SelectField("MDF file A", choices=[])
    mdf_b = SelectField("MDF file B", choices=[])
    submit = SubmitField("Get Diff")


class EditNodeForm(FlaskForm):
    nodeHandle = StringField('Handle', validators=[InputRequired(message="cannot be blank"), Length(min=0, max=140, message="length of handle must be greater than 0 and less than 140 characters")])
    submit = SubmitField("Save Changes")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    post = TextAreaField(_l("Say something"), validators=[DataRequired()])
    submit = SubmitField(_l("Submit"))


class SearchForm(FlaskForm):
    q = StringField(_l("Search"), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)
