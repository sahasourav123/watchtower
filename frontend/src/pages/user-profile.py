from dateutil import parser
import streamlit as st

import auth
from svc import svc_user_api as user_api
from svc import svc_backend as backend

st.set_page_config(layout='wide', page_title='User Profile', initial_sidebar_state='expanded')
st.title("User Profile")
user_code = auth.who_am_i()

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
    | Member Since | {parser.parse(user['ts_created']).strftime('%Y-%m-%d')}
    """)

with cc[1]:
    st.image(user['avatar'], width=300)

# API Tokens
st.divider()
cc = st.columns([3, 1])
token_df = backend.fetch_tokens(user_code)

with cc[1]:
    # Create Token
    st.subheader("Create New Token")
    name = st.text_input("Token Name")
    permission = st.radio("Permission", ['read-only', 'read-write'], horizontal=True)
    expiry_days = st.number_input("Expiry Days", min_value=1, max_value=365, value=60)
    if st.button(":material/add: Create Token"):
        res = backend.create_token(user_code, name, permission, expiry_days)
        st.rerun()

with cc[0]:
    st.subheader(f"Show Token [{token_df.shape[0]}]")
    # Show Tokens
    column_config = {
        'name': 'Name',
        'permission': 'Permission',
        'token': 'Token',
    }

    if not token_df.empty:
        selected_row = st.dataframe(token_df, hide_index=True, column_config=column_config, column_order=column_config.keys(), selection_mode=["single-row"], on_select='rerun')
        selected_row_index = selected_row['selection']['rows'][0] if selected_row['selection']['rows'] else None

        if selected_row_index is None:
            st.write(":blue[*select row to delete*]")
        else:
            selected_token = token_df.iloc[selected_row_index]

            if st.button(":material/delete: Delete Token"):
                backend.delete_token(user_code, selected_token['token'])
                st.rerun()
    else:
        st.info("No Tokens created yet")

