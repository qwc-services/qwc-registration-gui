from datetime import datetime

from flask import abort, flash, Flask, redirect, render_template, url_for
from sqlalchemy.orm import joinedload

from qwc_config_db.config_models import ConfigModels
from qwc_services_core.database import DatabaseEngine
from forms import RegistrationForm


class RegistrationGUI:
    """RegistrationGUI class

    Provide application form for group membership and create registration
    requests.
    """

    def __init__(self, logger):
        """Constructor

        :param Logger logger: Application logger
        """
        self.logger = logger

        # load ORM models for ConfigDB
        self.db_engine = DatabaseEngine()
        self.config_models = ConfigModels(self.db_engine)

        self.RegistrableGroup = self.config_models.model('registrable_groups')
        self.RegistrationRequest = self.config_models.model(
            'registration_requests'
        )
        self.User = self.config_models.model('users')

    def register(self, identity):
        """Show application form and submit membership requests.

        :param obj identity: User identity
        """
        # check if user is signed in
        username = self.username(identity)
        if username is None:
            self.logger.info("User is not signed in")
            abort(403)

        session = self.session()

        # find user
        user = session.query(self.User).filter_by(name=username).first()
        if user is None:
            self.logger.warning("Could not find user '%s'" % username)
            abort(404)

        # query registrable groups
        query = session.query(self.RegistrableGroup) \
            .order_by(self.RegistrableGroup.title)
        # eager load relations
        query = query.options(joinedload(self.RegistrableGroup.group))
        registrable_groups = query.all()

        # query pending registration requests for this user
        query = session.query(self.RegistrationRequest) \
            .filter_by(user_id=user.id, pending=True)
        pending_requests = query.all()
        pending_registrable_ids = [
            r.registrable_group_id for r in pending_requests
        ]

        # query group memberships
        user_groups = user.sorted_groups
        user_group_ids = [g.id for g in user_groups]

        session.close()

        # create form
        form = RegistrationForm()

        form.registrable_groups = []
        form.groups.choices = []
        form.unsubscribe_groups.choices = []
        for registrable_group in registrable_groups:
            pending = registrable_group.id in pending_registrable_ids
            member = registrable_group.group_id in user_group_ids

            # add registrable group
            form.registrable_groups.append({
                'id': registrable_group.id,
                'title': registrable_group.title,
                'description': registrable_group.description,
                'pending': pending,
                'member': member
            })

            if not pending:
                if member:
                    # add unsubscribable group choice
                    form.unsubscribe_groups.choices.append(
                        (registrable_group.id, registrable_group.title)
                    )
                else:
                    # add registrable group choice
                    form.groups.choices.append(
                        (registrable_group.id, registrable_group.title)
                    )

        if form.is_submitted():
            if form.validate():
                if form.groups.data or form.unsubscribe_groups.data:
                    # use same creation time for all requests in the form
                    created_at = datetime.utcnow()

                    session = self.session()

                    # create registration requests
                    for registrable_group_id in form.groups.data:
                        registration_request = self.RegistrationRequest(
                            user_id=user.id,
                            registrable_group_id=registrable_group_id,
                            unsubscribe=False,
                            pending=True,
                            created_at=created_at
                        )
                        session.add(registration_request)

                    # create unsubscribe requests
                    for registrable_group_id in form.unsubscribe_groups.data:
                        registration_request = self.RegistrationRequest(
                            user_id=user.id,
                            registrable_group_id=registrable_group_id,
                            unsubscribe=True,
                            pending=True,
                            created_at=created_at
                        )
                        session.add(registration_request)

                    session.commit()
                    session.close()

                    flash('Application form submitted', 'success')
                    return redirect(url_for('register'))
                else:
                    flash('No group selected', 'warning')
            else:
                self.logger.warning(form.errors)
                flash('Failed to submit application form', 'error')

        return render_template(
            'registration.html', title="Group Registration", form=form,
            username=user.name
        )

    def username(self, identity):
        """Extract username from identity.

        :param obj identity: User identity
        """
        username = None
        if isinstance(identity, dict):
            username = identity.get('username')
        else:
            # identity is username
            username = identity

        return username

    def session(self):
        """Return new session for ConfigDB."""
        return self.config_models.session()
