from datetime import datetime, timedelta
import jwt
from jwt import DecodeError, InvalidSignatureError
import streamlit as st
from streamlit_cookies_manager import CookieManager

class CookieModel:
    """
    This class executes the logic for the cookies for password-less re-authentication, 
    including deleting, getting, and setting the cookie.
    """

    def __init__(self, cookie_name: str, cookie_key: str, cookie_expiry_days: float):
        self.cookie_name = cookie_name
        self.cookie_key = cookie_key
        self.cookie_expiry_days = cookie_expiry_days
        self.cookie_manager = CookieManager()
        self.token = None
        self.exp_date = None

    def delete_cookie(self):
        """
        Deletes the re-authentication cookie.
        """
        try:
            self.cookie_manager.pop(self.cookie_name, None)
        except KeyError as e:
            print(e)

    def get_cookie(self) -> str:
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False and 'username' in self.token and self.token['exp_date'] > datetime.now().timestamp():
                return self.token['username']
        return None

    def set_cookie(self):
        if self.cookie_expiry_days != 0:
            self.exp_date = (datetime.now() + timedelta(days=self.cookie_expiry_days)).timestamp()
            token = self._token_encode()
            self.cookie_manager[self.cookie_name] = token

    def _token_decode(self) -> str:
        try:
            return jwt.decode(self.token, self.cookie_key, algorithms=['HS256'])
        except (DecodeError, InvalidSignatureError) as e:
            print(e)
            return False

    def _token_encode(self) -> str:
        return jwt.encode({'username': st.session_state['username'], 'exp_date': self.exp_date}, self.cookie_key, algorithm='HS256')
