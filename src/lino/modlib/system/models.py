## Copyright 2009-2010 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth import models as auth
from django.contrib.sessions import models as sessions
from django.contrib.contenttypes import models as contenttypes

#~ from django import forms
from django.db import models
from django.utils.translation import ugettext as _

import lino
from lino import reports
from lino import forms
from lino import layouts
from lino import actions
from lino import commands
from lino.utils import perms


class Permissions(reports.Report):
    model = auth.Permission
    order_by = 'content_type__app_label codename'
  
class Users(reports.Report):
    model = auth.User
    order_by = "username"
    display_field = 'username'
    column_names = 'username first_name last_name is_active id is_superuser is_staff last_login'

class Groups(reports.Report):
    model = auth.Group
    order_by = "name"
    display_field = 'name'

class Sessions(reports.Report):
    model = sessions.Session
    display_field = 'session_key'


class ContentTypes(reports.Report):
    model = contenttypes.ContentType



class PasswordReset(actions.OK):
    #~ layout = PasswordResetLayout
    title = _("Request Password Reset")
    
    def run_in_dlg(self,dlg):
        yield dlg.cancel('not implemented')
        yield dlg.show_modal_form(PasswordResetForm())


class PasswordResetForm(layouts.FormLayout):
    actions = [ actions.Cancel, PasswordReset]
    #~ datalink = 'system.PasswordReset'
    #email = models.EmailField(verbose_name=_("E-mail"), max_length=75)
    email = forms.Input(fieldLabel=_("E-mail"),maxLength=75)
    #~ ok = PasswordResetOK()
    label = _("Request Password Reset")
    
    intro = layouts.StaticText("""
    Please fill in your e-mail adress.
    We will then send you a mail with a new temporary password.
    """)
    
    main = """
    intro
    email:50
    ok cancel
    """
    
        
    
from django.contrib.auth import login, authenticate, logout


#~ class Login(commands.Command):
class Login(actions.OK):

    label = _("Login")
    
    def run_in_dlg(self,dlg):
      
        fh = dlg.get_form('LoginForm')
        yield dlg.show_modal_form(fh) 
        
        while True:
            if dlg.modal_exit != 'ok':
                yield dlg.cancel()
        
            username = fh.get_value('username')
            password = fh.get_value('password')
            #~ print username,password
            user = authenticate(username=username, password=password)
            if user is None:
                #~ raise actions.ValidationError(
                yield dlg.notify(
                _(u"Please enter a correct username and password. Both fields are case-sensitive."))
            elif not user.is_active:
                #~ raise actions.ValidationError(_("This account is inactive."))
                yield dlg.notify(_("This account is inactive."))
            else:
                login(dlg.request, user)
                #lino.log.info("User %s logged in.",user)
                yield dlg.ok("Welcome, %s!" % user).refresh_menu()



class LoginForm(layouts.FormLayout):
    #~ datalink = 'Login'
    actions = [ actions.Cancel, Login]
    
    text = layouts.StaticText(_("Please enter your username and password to authentificate."))
    username = forms.Input(fieldLabel=_("Username"),maxLength=75,allowBlank=False)
    password = forms.Input(fieldLabel=_("Password"),maxLength=75,inputType='password',allowBlank=False)
  
    main = """
    text
    username
    password
    _ cancel ok
    """


class Logout(commands.Command): #actions.OK):
  
    label = _("Log out")
    
    def run_in_dlg(self,dlg):
        user = dlg.get_user()
        yield dlg.confirm(_("%s, are you sure you want to log out?") % user)
        logout(dlg.request)
        yield dlg.notify("Goodbye, %s!" % user).refresh_menu().over()

    


def add_auth_menu(lino):
    if False:
        m = lino.add_menu("auth",_("~Authentificate"))
        m.add_action('system.Login',can_view=perms.is_anonymous)
        m.add_action('system.Logout',can_view=perms.is_authenticated)
        m.add_action('system.PasswordReset',can_view=perms.is_authenticated)
