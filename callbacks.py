import dash
import dash_html_components as html
from dash.dependencies import Output, Input, State
from flask_login import login_user, logout_user, current_user, UserMixin
from werkzeug.security import check_password_hash

from app import app
from layouts.login import login_layout, logout_layout, create_account_layout
from layouts.authenticated_content import authenticated_content
from users_utils import diabUser as base, db, add_user

class User(UserMixin, base):
    pass

@app.callback(
        [
            Output('page-content', 'children'),
            Output("header-logout", "style"),
            Output("uname-display", "children")
            ],
        [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return login_layout, {"display": "none"}, dash.no_update
    elif pathname == '/login':
        return login_layout, {"display": "none"}, dash.no_update
    elif pathname == '/success':
        if current_user.is_authenticated:
            return (
                    authenticated_content,
                    {"display": "flex"},
                    f"Welcome {current_user.username}"
                    )
        else:
            return login_layout, {"display": "none"}, dash.no_update
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout_layout, {"display": "none"}, dash.no_update
        else:
            return logout_layout, {"display": "none"}, dash.no_update
    elif pathname == "/create-account":
        return (
                create_account_layout,
                {"display": "flex"},
                "Create an Account"
                )
    else:
        return '404'

@app.callback(
        Output('url_login', 'pathname'),
        [
            Input('login-button', 'n_clicks'),
            Input("pwd-box", "value"),
            Input("create-account-button", "n_clicks")
            ],
        [State('uname-box', 'value'), State("url_login", "pathname")])
def success(n_clicks, password, create_click, uname, old_url):
    if old_url == "/success":
        return "/login"
    if create_click:
        return "/create-account"
    if not uname or uname == "":
        return dash.no_update
    user = User.query.filter_by(username=uname).first()
    if user:
        if check_password_hash(user.password, password):
            login_user(user)
            return "/success"
        else:
            return "/login"
    else:
        return "/login"


@app.callback(
        Output('url_logout', 'pathname'),
        [Input('re-login-button', 'n_clicks')],
        )
def relogin(n_clicks):
    if n_clicks > 0:
        return "/login"


@app.callback(
        Output("url", "pathname"),
        [Input("logout-button", "n_clicks")]
        )
def url_logout(n_clicks):
    if n_clicks:
        return "/logout"


@app.callback(
        [Output("url_create", "pathname"), Output("create-error", "children")],
        [Input("create-account-submit", "n_clicks")],
        [
            State("create-uname-box", "value"),
            State("create-pwd-box", "value"),
            State("confirm-pwd-box", "value"),
            State("create-email-box", "value")
        ]
        )
def add_new_user(n_clicks, uname, pw, pw_conf, email):
    if n_clicks:
        if pw != pw_conf:
            return dash.no_update, "Passwords don't match!"
        add_user(uname, pw, email)
        return "/login", dash.no_update
