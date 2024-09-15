from dateutil import parser
import pandas as pd
import streamlit as st

import auth
from svc import svc_user_api as user_api

st.title("User Profile")
user_code = auth.ensure_logged_in(required_access_level='user')

user = user_api.get_user(user_code)
st.write(f"### Hello, {user['user_name'].split()[0]} !")

# show user avatar & email
cc = st.columns(2)
with cc[0]:
    # Display user details in a formatted manner
    st.markdown(f"""
    | User Code | {user['user_code']} |
    |----|---|
    | User Name | {user['user_name']} |
    | Email | {user['email']} |
    | Phone | {user['user_mobile']} |
    | Role | {user['privilege'].upper()} |
    | Status | {user['status'].upper()} |
    | Member Since | {parser.parse(user['ts_created']).strftime('%Y-%m-%d')}
    """)

with cc[1]:
    st.image(user['avatar'], width=300)

