from dateutil import parser
import streamlit as st

import auth
from svc import svc_user_api as user_api

st.set_page_config(layout='wide', page_title='User Profile', initial_sidebar_state='expanded')
st.title("User Profile")
user_code = auth.ensure_logged_in()

if user_code == 'guest':
    st.warning("Please login to view your profile.")
    st.stop()

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
    | Org Codes | {', '.join([f'`{org}`' for org in user['org_codes']])} |
    | Member Since | {parser.parse(user['ts_created']).strftime('%Y-%m-%d')}
    """)

with cc[1]:
    st.image(user['avatar'], width=300)

