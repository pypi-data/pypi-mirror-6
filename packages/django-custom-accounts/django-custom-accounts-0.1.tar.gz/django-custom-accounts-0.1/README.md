# Django Custom Accounts

## Install

Via pip

    pip install django-custom-accounts

Via easy\_install

    easy_install django-custom-accounts

## Usage

### Settings

In settings.py add:

    INSTALLED_APPS = (
        ...
        'accounts'
        ...
    )

    AUTH_USER_MODEL = 'accounts.CustomUser'

    CUSTOM_AUTH_ACTIVATION_EMAIL = True # if True sent an email to activate your account otherwise the account is activate automatically
    CUSTOM_AUTH_AUTO_LOGIN = True # if true the user is logged automatically after registration or confirming
    CUSTOM_AUTH_REGISTER_REDIRECT_URL = None # String with the url to redirect after successful registration
    CUSTOM_AUTH_CONFIRM_REDIRECT_URL = None # String with the url to redirect after successful confirmation
    LOGIN_REDIRECT_URL = '/accounts/profile/' # String with the url to redirect after login
    LOGOUT_REDIRECT_URL = None # String with the url to redirect after logout


In urls.py add:

    url(r'^accounts/', include('accounts.urls')),


### Templates

List of templates for auth.
All the templates go in registration folder

- login.html: Template for login form.
- logged\_out: Template por logout success message.
- register\_form.html: Template for registration form.
- activation\_email.html: Template for email confirmation.
- activation\_subject.txt: Template for email confirmation subject.
- activation\_confirm.html: Template for successful and unsuccesseful confirmation message.
- password\_reset\_form.html: Template for recovery password form.
- password\_reset\_email.html: Template for recovery password email.
- password\_reset\_subject.txt: Template for recovery password email subject.
- password\_reset\_done.html: Template for recovery password done. (Request mail for recovery password message)
- password\_reset\_confirm.html: Template for change password form.
- password\_reset\_complete.html Template for changge passowrd success message.


## Todo

- Tests
- Facebook login/auth suppport
- Twitter login/auth support


## Changelog

### 0.1 - 2014-04-22  Alvaro Lizama  <nekrox@gmail.com>

- First release


## License

Copyright (c) 2014 Alvaro Lizama Molina

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
