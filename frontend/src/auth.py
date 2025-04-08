import os

import streamlit as st
from svc import svc_user_api as user_api

import utils
import logging
logger = logging.getLogger()

def _default_user():
    user_code = os.environ.get('DEFAULT_USER', 'guest')
    st.session_state['org_code'] = []
    st.sidebar.write(f"User: **{user_code}**")
    return user_code

def who_am_i():
    with st.sidebar:
        utils.page_navigation_menu()

        if not st.experimental_user.is_logged_in:
            if st.button("Google Sign In"):
                st.login()
                print(f"Logging in...")
            print(f"Not logged in")
            return _default_user()

        else:
            _users_ = user_api.get_users({'user_email': st.experimental_user.email})

            if not _users_ or len(_users_) == 0:
                logger.info(f"Creating new user with email: {st.experimental_user.email}")
                # create user in db
                _user_ = user_api.create_user({
                    "user_name": st.experimental_user.name,
                    "user_email": st.experimental_user.email,
                    "avatar": st.experimental_user.picture,
                    "auth_providers": ['google']
                })
                logger.info(f"New User Created: {_user_}")
                user_code = _user_.get('user_code')
            else:
                user_code = _users_[0].get('user_code')

            st.divider()
            print(f"Logged in: {user_code}")
            st.markdown(f"User Code: {user_code}")

            if st.button("Log out"):
                print(f"Logging out...")
                st.logout()

            return user_code
