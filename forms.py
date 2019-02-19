from flask_wtf import FlaskForm
from wtforms import SelectMultipleField
from wtforms.validators import DataRequired, Optional


class RegistrationForm(FlaskForm):
    """list of registrable groups

        [
            {
                'id': <id>,
                'title': '<title>',
                'description': '<description>',
                'pending': <True if pending>,
                'member': <True if already a group member>
            }
        ]
    """
    registrable_groups = []
    # requestable groups
    groups = SelectMultipleField(
        'Groups',
        coerce=int, validators=[Optional()]
    )
    # unsubscribable groups
    unsubscribe_groups = SelectMultipleField(
        'Unsubscribable Groups',
        coerce=int, validators=[Optional()]
    )
