__author__ = 'sarsanaee'

from flask_admin.contrib.sqla import ModelView
import flask_wtf
from flask import url_for, redirect, request
from wtforms import form, fields, validators
from flask.ext import admin, login
from flask.ext.admin.contrib import sqla
from flask.ext.admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash

from database import db_session
from models import AdminUsers


class ApiView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

class GameDbView(ModelView):
    column_display_pk = True

    def is_accessible(self):
        return login.current_user.is_authenticated()

class SpecialPackView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class StoreView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class XmlBaseView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class TransactionView(ModelView):
    column_searchable_list = ['token']
    page_size = 100


    def is_accessible(self):
        return login.current_user.is_authenticated()

class GiftCardView(ModelView):
    form_base_class = flask_wtf.Form
    form_columns = ('code', 'count', 'diamond_count')
    can_export = True

    def is_accessible(self):
        return login.current_user.is_authenticated()



class UserView(ModelView):
    form_base_class = flask_wtf.Form
    form_columns = ('username',
                    'email',
                    'password',
                    'register_date',
                    'last_check',
                    'total_level',
                    'shop',
                    'score',
                    'gold',
                    'diamond',
                    'chars_bought',
                    'is_banned',
                    'wins',
                    'last_daily_reward_date',
                    'daily_reward_with_price_count',
                    'daily_reward_with_price_date')

    column_exclude_list = ('chars',
                           'status',
                           'trans')
    column_sortable_list = ('shop',
                            'gold',
                            'diamond',
                            'score',
                            'total_level',
                            'id',
                            'username')
    column_searchable_list = ['username',
                              'email']
    column_filters = ['gold',
                      'diamond',
                      'score',
                      'shop',
                      'total_level']
    page_size = 100
    column_display_pk = True
    can_export = False
    can_edit = True

    column_formatters = dict(username=lambda v, c, m, p: m.username if all(ord(c) < 128 for c in m.username) else m.username[::-1])

    def is_accessible(self):
        return login.current_user.is_authenticated()


class LevelView(ModelView):
    form_base_class = flask_wtf.Form
    column_sortable_list = ('level', 'time')
    column_searchable_list = ['user_id', 'level', 'time']
    column_filters = ['user_id', 'level', 'time']
    page_size = 100
    can_export = True
    can_edit = True

    #column_formatters = dict(Users=lambda v, c, m, p: m.Users if all(ord(c) < 128 for c in m.Users) else m.Users[::-1])

    form_columns = ['level', 'time', 'user_id']

    def is_accessible(self):
        return login.current_user.is_authenticated()


class AdminUsersView(ModelView):
    form_base_class = flask_wtf.Form

    def is_accessible(self):
        return login.current_user.is_authenticated()


class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db_session.query(AdminUsers).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db_session.query(AdminUsers).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')





# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated()


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    #############################################
    @expose('/register/', methods=('GET', 'POST'))#, 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = AdminUsers()
            form.populate_obj(user)
            user.password = generate_password_hash(form.password.data)
            db_session.add(user)
            db_session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()



    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))