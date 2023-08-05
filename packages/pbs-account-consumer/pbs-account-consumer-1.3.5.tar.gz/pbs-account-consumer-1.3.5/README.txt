Installation
============
`pip install pbs-account-consumer`

Configuration
=============
1. Add `pbs_account_consumer` to the INSTALLED_APPS section of the settings file.

2. After installing you need to add a couple of params to your settings.py file.

    * **Example param values:**
        - OPENID_SSO_SERVER_URL = 'https://account.pbs.org/cranky'                                                                                                                    
        - OPENID_CREATE_USERS = True                                                                                                                                                     
        - OPENID_UPDATE_DETAILS_FROM_SREG = True                                                                                                                                         
        - OPENID_USE_AS_ADMIN_LOGIN = True                                                                                                                                               
        - OPENID_ADMIN_LOGIN_TEMPLATE = None                                                                                                                                             
        - LOGIN_REDIRECT_URL = '/'    

3. Add the consumer app to the url routing.

    * **For example:**
        - Add `url(r'^openid/', include('pbs_account_consumer.urls'))` to urls.py in your project.

4. Add the proper authentication backend to your project.

    - Add `AUTHENTICATION_BACKENDS = (..., 'pbs_account_consumer.auth.OpenIDBackend',)` to settings.py.

5. Add the proper login link to the admin login template:

    - Add `pbs_accout_consumer.urls` to the main urls.py file of your project.

    - Make the link point to the `login_begin` view, as such: `{% url login_begin %}`

6. (Optional) If you want to use a custom realm (eg. you don't want it to point
to the base of your domain) you have to set OPENID_CUSTOM_REALM in settings.py:

    OPENID_CUSTOM_REALM = 'https://mysite.com/realm'

The default is the absolute URI of the base of your website.

7. (Optional) If you want to use a custom domain (eg. if you are using a proxy for your
website) for the `return_to` page you can set OPENID_CUSTOM_RETURN_TO in settings.py:

    OPENID_CUSTOM_RETURN_TO = 'https://mysite.com/realm/landing'

The return_to parameter of the OpenID request will be set to `login_route` route, 
relative to this parameter. 
The default is the absolute URI of the base of your website. 

The RETURN_TO url should be under the REALM (trust_root), otherwise the OpenID
provider will give an error and disallow authentication.

8. (Optional) If you need to know whether a user verified his email address you have
to add to settings.py file:

    AX_FETCH_IS_VERIFIED = True

OpenIDBackend
=============

To check if a user has a verified email address, use _get_is_verified() method from backend.
Also, is a user should not be allowed to login with an unverified email, subclass OpenIDBackend,
override create_user_from_openid and set on the user object the attribute requires_verified_email
to True:

    class MyOpenIDBackend(OpenIDBackend):
        def create_user_from_openid(self, openid_response):
            ...
            if condition:
                if not self._get_is_verified(openid_response):
                    user.requires_verified_email = True
                    return user
            ...

Requirments
===========
1. Python version 2.7 or greater.
2. Django version 1.3 or greater.
