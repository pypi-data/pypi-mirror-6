# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid.view import view_config
from pyramid.url import route_url
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.settings import asbool

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from hem.db import get_session
from horus.interfaces import IUserClass
from horus.interfaces import IActivationClass
from horus.interfaces import IUIStrings
from horus.interfaces import ILoginForm
from horus.interfaces import ILoginSchema
from horus.interfaces import IRegisterForm
from horus.interfaces import IRegisterSchema
from horus.interfaces import IForgotPasswordForm
from horus.interfaces import IForgotPasswordSchema
from horus.interfaces import IResetPasswordForm
from horus.interfaces import IResetPasswordSchema
from horus.interfaces import IProfileForm
from horus.interfaces import IProfileSchema
from horus.events import NewRegistrationEvent
from horus.events import RegistrationActivatedEvent
from horus.events import PasswordResetEvent
from horus.events import ProfileUpdatedEvent
from horus.lib import FlashMessage
from horus.models import _
from horus.exceptions import AuthenticationFailure
from horus.httpexceptions import HTTPBadRequest

import colander
import deform
import pystache


def get_config_route(request, config_key):
    settings = request.registry.settings

    try:
        return request.route_url(settings[config_key])
    except KeyError:
        return settings[config_key]


def authenticated(request, userid):
    """Sets the auth cookies and redirects to the page defined
    in horus.login_redirect, which defaults to a view named 'index'.
    """
    settings = request.registry.settings
    headers = remember(request, userid)
    autologin = asbool(settings.get('horus.autologin', False))

    if not autologin:
        Str = request.registry.getUtility(IUIStrings)
        FlashMessage(request, Str.authenticated, kind='success')

    location = get_config_route(request, 'horus.login_redirect')

    return HTTPFound(location=location, headers=headers)


def create_activation(request, user):
    db = get_session(request)
    Activation = request.registry.getUtility(IActivationClass)
    activation = Activation()

    db.add(activation)
    user.activation = activation

    db.flush()

    # TODO Create a hook for the app to give us body and subject!
    # TODO We don't need pystache just for this!
    body = pystache.render(
        _("Please validate your email and activate your account by visiting:\n"
            "{{ link }}"),
        {
            'link': request.route_url('activate', user_id=user.id,
                                      code=user.activation.code)
        }
    )
    subject = _("Please activate your account!")

    message = Message(subject=subject, recipients=[user.email], body=body)
    mailer = get_mailer(request)
    mailer.send(message)


class BaseController(object):
    @property
    def request(self):
        # we defined this so that we can override the request in tests easily
        return self._request

    def __init__(self, request):
        self._request = request
        self.settings = request.registry.settings
        getUtility = request.registry.getUtility
        self.User = getUtility(IUserClass)
        self.Activation = getUtility(IActivationClass)
        self.Str = getUtility(IUIStrings)
        self.db = get_session(request)


class AuthController(BaseController):
    def __init__(self, request):
        super(AuthController, self).__init__(request)

        schema = request.registry.getUtility(ILoginSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(ILoginForm)

        self.login_redirect_view = get_config_route(
            request,
            'horus.login_redirect'
        )

        self.logout_redirect_view = get_config_route(
            request,
            'horus.logout_redirect'
        )

        self.require_activation = asbool(
            self.settings.get('horus.require_activation', True)
        )
        self.allow_inactive_login = asbool(
            self.settings.get('horus.allow_inactive_login', False)
        )
        self.form = form(self.schema, buttons=(self.Str.login_button,))

    def check_credentials(self, username, password):
        allow_email_auth = self.settings.get('horus.allow_email_auth', False)

        user = self.User.get_user(self.request, username, password)

        if allow_email_auth and not user:
            user = self.User.get_by_email_password(
                self.request, username, password)

        if not user:
            raise AuthenticationFailure(_('Invalid username or password.'))

        if not self.allow_inactive_login and self.require_activation \
                and not user.is_activated:
            raise AuthenticationFailure(
                _('Your account is not active, please check your e-mail.'))
        return user

    @view_config(route_name='login', xhr=True, accept="application/json",
                 renderer='json')
    def login_ajax(self):
        try:
            cstruct = self.request.json_body
        except ValueError as e:
            raise HTTPBadRequest({'invalid': str(e)})

        try:
            captured = self.schema.deserialize(cstruct)
        except colander.Invalid as e:
            raise HTTPBadRequest({'invalid': e.asdict()})

        username = captured['username']
        password = captured['password']

        try:
            user = self.check_credentials(username, password)
        except AuthenticationFailure as e:
            raise HTTPBadRequest({
                'status': 'failure',
                'reason': e.message,
            })

        # We pass the user back as well so the authentication
        # can use its security code or any other information stored
        # on the user
        user_json = user.__json__(self.request)

        return {'status': 'okay',
                'user': user_json}

    @view_config(route_name='login', renderer='horus:templates/login.mako')
    def login(self):
        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.login_redirect_view)
            return {'form': self.form.render()}

        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure as e:
                return {
                    'form': e.render(),
                    'errors': e.error.children
                }

            username = captured['username']
            password = captured['password']

            try:
                user = self.check_credentials(username, password)
            except AuthenticationFailure as e:
                FlashMessage(self.request, str(e), kind='error')
                return {
                    'form': self.form.render(appstruct=captured),
                    'errors': [e]
                }

            self.request.user = user  # Please keep this line, my app needs it

            return authenticated(self.request, user.id_value)

    @view_config(permission='view', route_name='logout')
    def logout(self):
        """Removes the auth cookies and redirects to the view defined in
        horus.logout_redirect, which defaults to a view named 'index'.
        """
        self.request.session.invalidate()
        FlashMessage(self.request, self.Str.logout, kind='success')
        headers = forget(self.request)
        return HTTPFound(location=self.logout_redirect_view, headers=headers)


class ForgotPasswordController(BaseController):
    def __init__(self, request):
        super(ForgotPasswordController, self).__init__(request)

        self.forgot_password_redirect_view = route_url(
            self.settings.get('horus.forgot_password_redirect', 'index'),
            request)
        self.reset_password_redirect_view = route_url(
            self.settings.get('horus.reset_password_redirect', 'index'),
            request)

    @view_config(route_name='forgot_password',
                 renderer='horus:templates/forgot_password.mako')
    def forgot_password(self):
        req = self.request
        schema = req.registry.getUtility(IForgotPasswordSchema)
        schema = schema().bind(request=req)

        form = req.registry.getUtility(IForgotPasswordForm)
        form = form(schema)

        if req.method == 'GET':
            if req.user:
                return HTTPFound(location=self.forgot_password_redirect_view)
            else:
                return {'form': form.render()}

        # From here on, we know it's a POST. Let's validate the form
        controls = req.POST.items()
        try:
            captured = form.validate(controls)
        except deform.ValidationFailure as e:
            # This catches if the email does not exist, too.
            return {'form': e.render(), 'errors': e.error.children}

        user = self.User.get_by_email(req, captured['email'])
        activation = self.Activation()
        self.db.add(activation)
        user.activation = activation
        Str = self.Str

        # TODO: Generate msg in a separate method so subclasses can override
        mailer = get_mailer(req)
        username = getattr(user, 'short_name', '') or \
            getattr(user, 'full_name', '') or \
            getattr(user, 'username', '') or user.email
        body = Str.reset_password_email_body.format(
            link=route_url('reset_password', req, code=user.activation.code),
            username=username, domain=req.application_url)
        subject = Str.reset_password_email_subject
        message = Message(subject=subject, recipients=[user.email], body=body)
        mailer.send(message)

        FlashMessage(self.request, Str.reset_password_email_sent,
            kind='success')
        return HTTPFound(location=self.reset_password_redirect_view)

    @view_config(route_name='reset_password',
                 renderer='horus:templates/reset_password.mako')
    def reset_password(self):
        schema = self.request.registry.getUtility(IResetPasswordSchema)
        schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(IResetPasswordForm)
        form = form(schema)

        code = self.request.matchdict.get('code', None)

        activation = self.Activation.get_by_code(self.request, code)

        if activation:
            user = self.User.get_by_activation(self.request, activation)

            if user:
                if self.request.method == 'GET':
                    return {
                        'form': form.render(
                            appstruct=dict(
                                username=user.username
                            )
                        )
                    }

                elif self.request.method == 'POST':
                    try:
                        controls = self.request.POST.items()
                        captured = form.validate(controls)
                    except deform.ValidationFailure as e:
                        return {'form': e.render(), 'errors': e.error.children}

                    password = captured['password']

                    user.password = password
                    self.db.add(user)
                    self.db.delete(activation)

                    FlashMessage(self.request, self.Str.reset_password_done,
                                 kind='success')
                    self.request.registry.notify(PasswordResetEvent(
                        self.request, user, password))
                    location = self.reset_password_redirect_view
                    return HTTPFound(location=location)
        return HTTPNotFound()


class RegisterController(BaseController):
    def __init__(self, request):
        super(RegisterController, self).__init__(request)
        schema = request.registry.getUtility(IRegisterSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(IRegisterForm)
        self.form = form(self.schema)

        self.after_register_url = route_url(
            self.settings.get('horus.register_redirect', 'index'), request)
        self.after_activate_url = route_url(
            self.settings.get('horus.activate_redirect', 'index'), request)

        self.require_activation = asbool(
            self.settings.get('horus.require_activation', True))

        if self.require_activation:
            self.mailer = get_mailer(request)

    @view_config(route_name='register',
                 renderer='horus:templates/register.mako')
    def register(self):
        if self.request.method == 'GET':
            if self.request.user:
                return HTTPFound(location=self.after_register_url)
            return {'form': self.form.render()}
        elif self.request.method != 'POST':
            return

        # If the request is a POST:
        controls = self.request.POST.items()
        try:
            captured = self.form.validate(controls)
        except deform.ValidationFailure as e:
            return {'form': e.render(), 'errors': e.error.children}

        # With the form validated, we know email and username are unique.
        del captured['csrf_token']
        user = self.persist_user(captured)

        autologin = asbool(self.settings.get('horus.autologin', False))

        if self.require_activation:
            # SEND EMAIL ACTIVATION
            create_activation(self.request, user)
            FlashMessage(self.request, self.Str.activation_check_email,
                         kind='success')
        elif not autologin:
            FlashMessage(self.request, self.Str.registration_done,
                         kind='success')

        self.request.registry.notify(NewRegistrationEvent(
            self.request, user, None, controls))
        if autologin:
            self.db.flush()  # in order to get the id
            return authenticated(self.request, user.id)
        else:  # not autologin: user must log in just after registering.
            return HTTPFound(location=self.after_register_url)

    def persist_user(self, controls):
        '''To change how the user is stored, override this method.'''
        # This generic method must work with any custom User class and any
        # custom registration form:
        user = self.User(**controls)
        self.db.add(user)
        return user

    @view_config(route_name='activate')
    def activate(self):
        code = self.request.matchdict.get('code', None)
        user_id = self.request.matchdict.get('user_id', None)

        activation = self.Activation.get_by_code(self.request, code)

        if activation:
            user = self.User.get_by_id(self.request, user_id)

            if user.activation != activation:
                return HTTPNotFound()

            if user:
                self.db.delete(activation)
                # self.db.add(user)  # not necessary
                self.db.flush()
                FlashMessage(self.request, self.Str.activation_email_verified,
                             kind='success')
                self.request.registry.notify(
                    RegistrationActivatedEvent(self.request, user, activation))
                return HTTPFound(location=self.after_activate_url)
        return HTTPNotFound()


class ProfileController(BaseController):
    def __init__(self, request):
        super(ProfileController, self).__init__(request)

        schema = self.request.registry.getUtility(IProfileSchema)
        self.schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(IProfileForm)
        self.form = form(self.schema)

    @view_config(route_name='profile', renderer='horus:templates/profile.mako')
    def profile(self):
        user_id = self.request.matchdict.get('user_id', None)

        user = self.User.get_by_id(self.request, user_id)

        if not user:
            return HTTPNotFound()

        return {'user': user}

    @view_config(permission='access_user', route_name='edit_profile',
                 renderer='horus:templates/edit_profile.mako')
    def edit_profile(self):
        user = self.request.context

        if not user:
            return HTTPNotFound()

        if self.request.method == 'GET':
            username = user.username
            email = user.email

            return {
                'form': self.form.render(
                    appstruct=dict(
                        username=username,
                        email=email if email else '',
                    )
                )
            }
        elif self.request.method == 'POST':
            try:
                controls = self.request.POST.items()
                captured = self.form.validate(controls)
            except deform.ValidationFailure as e:
                # We pre-populate username
                e.cstruct['username'] = user.username
                return {'form': e.render(), 'errors': e.error.children}

            email = captured.get('email', None)

            if email:
                email_user = self.User.get_by_email(self.request, email)

                if email_user:
                    if email_user.id != user.id:
                        FlashMessage(self.request,
                            _('That e-mail is already used.'), kind='error')
                        return HTTPFound(location=self.request.url)

                user.email = email

            password = captured.get('password')

            if password:
                user.password = password

            FlashMessage(self.request, self.Str.edit_profile_done,
                         kind='success')

            self.db.add(user)

            self.request.registry.notify(
                ProfileUpdatedEvent(self.request, user, captured)
            )
            return HTTPFound(location=self.request.url)
