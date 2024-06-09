from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DomainForm(FlaskForm):
    domain = StringField('Domain', validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired()])
    submit = SubmitField('Submit')

class PortForm(FlaskForm):
    port = IntegerField('Port', validators=[DataRequired()])
    protocol = SelectField('Protocol', choices=[('tcp', 'TCP'), ('udp', 'UDP')], validators=[DataRequired()])
    duration = IntegerField('Duration (minutes)', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateForm(FlaskForm):
    update_key = StringField('Update Key', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=60)])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('user', 'User')], validators=[DataRequired()])
    submit = SubmitField('Submit')
