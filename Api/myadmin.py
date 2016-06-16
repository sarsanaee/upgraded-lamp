__author__ = 'sarsanaee'

from flask_admin.contrib.sqla import ModelView
import flask_wtf
from flask import url_for, redirect, request
from wtforms import form, fields, validators
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash
from Api.models import User
from Api.database import db_session
from Api.models import AdminUsers
import flask_login as login
import flask_admin as admin
from bidi import algorithm


class ApiView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

class OnlineServerView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated()

class GameDbView(ModelView):
    #column_display_pk = True
    create_modal = False
    can_export = True


    column_searchable_list = (
        (User.username),
        'XP'
    )
    column_exclude_list = ('LevelsStatus',
                           'LevelTimeStatus',
                           'FactoryLevel',
                           'Charecters',
                           'LevelTutorial1',
                           'LevelTutorial2',
                           'LevelTutorial3',
                           'MainMenuTutorial',
                           'MapTutorial_1',
                           'MapTutorial_2',
                           'username'
                           )
    can_view_details = True
    form_excluded_columns = ['users',]



    def is_accessible(self):
        return login.current_user.is_authenticated()

class SpecialPackView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class StoreView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class TransactionView(ModelView):
    column_searchable_list = (
        (User.username),
        'token'
    )
    page_size = 100
    column_default_sort = ('date', True)
    form_excluded_columns = ['users',]



    def is_accessible(self):
        return login.current_user.is_authenticated()

class GiftCardView(ModelView):
    form_base_class = flask_wtf.Form
    form_columns = ('code', 'count', 'diamond_count', 'username')
    can_export = True

    column_formatters = dict(username=lambda v, c, m, p: algorithm.get_display(m.username) if m.username else "")


    def is_accessible(self):
        return login.current_user.is_authenticated()



class UserView(ModelView):
    can_export = True
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
                    'lose',
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
    can_edit = True

    column_formatters = dict(username=lambda v, c, m, p: algorithm.get_display(m.username))#if all(ord(c) < 128 for c in m.username) else m.username[::-1])


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
    login = fields.StringField(validators=[validators.required()])
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
    @expose('/register/', methods=['GET'])#, 'POST'))
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
