import os
import jwt
import requests

import streamlit as st
from streamlit_oauth import OAuth2Component
from cookie_model import CookieModel

from svc import svc_user_api as user_api

import logging
logger = logging.getLogger()


class SessionManager:
    def __init__(self):
        self.cookie_model = CookieModel(
            cookie_name=os.getenv('COOKIE_NAME'),
            cookie_key=os.getenv('COOKIE_SECRET'),
            cookie_expiry_days=int(os.getenv('COOKIE_EXPIRY'))
        )

    def oauth(self):
        cc = st.columns(2)
        with cc[0]:
            # create an OAuth2Component instance
            logger.warning("Logging with OAuth2")
            google_oauth2 = OAuth2Component(
                client_id=os.environ.get("GOOGLE_CLIENT_ID"),
                client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
                authorize_endpoint=os.environ.get("GOOGLE_AUTHORIZE_ENDPOINT"),
                token_endpoint=os.environ.get("GOOGLE_TOKEN_ENDPOINT"),
                refresh_token_endpoint=os.environ.get("GOOGLE_TOKEN_ENDPOINT"),
                revoke_token_endpoint=os.environ.get("GOOGLE_REVOKE_ENDPOINT")
            )
            # create a button to start the OAuth2 flow
            google_result = google_oauth2.authorize_button(
                name="Continue with Google",
                icon="https://www.google.com.tw/favicon.ico",
                redirect_uri=os.environ.get("GOOGLE_REDIRECT_URL"),
                scope="openid email profile",
                key="google",
                extras_params={"prompt": "consent", "access_type": "offline"},
                # use_container_width=True,
                pkce='S256',
            )

            # print(f"google_result: {google_result}")
            if google_result:
                # decode the id_token jwt and get the user's email address
                jwt_token = google_result["token"]["id_token"]
                logged_in_user = jwt.decode(jwt_token, algorithms=["RS256"], options={"verify_signature": False})
                # print(logged_in_user)
                return {
                    "provider": "google",
                    "email": logged_in_user['email'],
                    "name": logged_in_user['name'],
                    "avatar": logged_in_user['picture']
                }

        with cc[1]:
            # create an OAuth2Component instance
            github_oauth2 = OAuth2Component(
                client_id=os.environ.get("GITHUB_CLIENT_ID"),
                client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
                authorize_endpoint=os.environ.get("GITHUB_AUTHORIZE_ENDPOINT"),
                token_endpoint=os.environ.get("GITHUB_TOKEN_ENDPOINT"),
                refresh_token_endpoint=os.environ.get("GITHUB_TOKEN_ENDPOINT")
            )
            # create a button to start the OAuth2 flow
            github_result = github_oauth2.authorize_button(
                name="Continue with Github",
                icon="https://github.githubassets.com/favicons/favicon.png",
                redirect_uri=os.environ.get("GITHUB_REDIRECT_URL"),
                scope="user,user:email",
                key="gituhb",
                # extras_params={"prompt": "select_account"},
                # use_container_width=True,
                pkce='S256',
            )

            # print(f"github_result: {github_result}")
            if github_result:
                access_token = github_result["token"]["access_token"]
                # get user from curl -H "Authorization: Bearer OAUTH-TOKEN" https://api.github.com/user
                res = requests.get("https://api.github.com/user", headers={"Authorization": f"Bearer {access_token}"})
                logged_in_user = res.json()
                # print(logged_in_user)
                return {
                    "provider": "github",
                    "email": logged_in_user['email'],
                    "name": logged_in_user['name'],
                    "avatar": logged_in_user['avatar_url']
                }

    def login(self):

        if st.session_state.get('username'):
            return st.session_state.get('username')

        token = self.cookie_model.get_cookie()
        if token:
            st.session_state['authentication_status'] = True
            st.session_state['username'] = token
            return token

        logged_in_user = self.oauth()
        if logged_in_user:
            # user_email = logged_in_user["email"]
            user_code = self._get_user_code(logged_in_user)

            st.session_state['username'] = user_code
            self.cookie_model.set_cookie()
            st.session_state['authentication_status'] = True
            st.rerun()

    def logout(self):
        # self.cookie_controller.clear_cookie()
        self.cookie_model.delete_cookie()
        st.session_state['authentication_status'] = False
        st.session_state['username'] = None
        st.success('Logged Out Successfully')

    def _get_user_code(self, logged_in_user):
        user_email = logged_in_user["email"]
        known_user = user_api.get_users({'user_email': user_email})
        # create profile page (if new user, ask for more details)
        if not known_user or len(known_user) == 0:
            logger.warning(f"Creating new user with email: {user_email}")

            # create user in db
            new_user = user_api.create_user({
                "user_name": logged_in_user.get("name"),
                "user_email": logged_in_user.get("email"),
                "avatar": logged_in_user.get("avatar"),
                "auth_providers": [logged_in_user.get("provider")]
            })
            logger.info(f"New User Created: {new_user}")
            return new_user['user_code']
        else:
            return known_user['user_code']

def ensure_logged_in(required_access_level='viewer'):
    print(f'Ensure Logged In with access level: {required_access_level}')
    sm = SessionManager()
    user_code = sm.login()

    if not user_code:
        st.error('Login Required')
        st.stop()

    with st.sidebar:
        st.write(f"User Code: {user_code}")
        if st.button('Logout'):
            sm.logout()
            st.rerun()

    # get_user_privilege
    user = user_api.get_user(user_code)
    privilege = user.get('privilege', 'viewer')
    print(f"Logged in: {user_code} | Privilege: {privilege}")

    if required_access_level == 'admin' and privilege != 'admin':
        st.error('This page is accessible with Admin privilege Only')
        st.stop()

    return user_code
