import re

import dash
import dash_html_components as html
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from flask_login import login_user, logout_user, current_user, UserMixin
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from app import app
from layouts.login import login_layout, logout_layout, create_account_layout
from layouts.authenticated_content import authenticated_content
from layouts.fitbit_layout import fitbit_tab_layout, fitbit_request_auth_layout
from db_utils import diabUser as base, db, add_user, send_conf_email, confirm_code
from utils.fitbit_auth import get_user_access_token
from utils.fitbit_api_calls import fitbit_heart


class User(UserMixin, base):
    pass


@app.callback(
    [
        Output("page-content", 'children'),
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
            ""
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
        message = ""
        if n_clicks > 1:
            message = "Enter a username pls"
        return dash.no_update
    user = User.query.filter_by(username=uname).first()
    if user:
        if check_password_hash(user.password, password):
            login_user(user)
            return "/success"
        else:
            return "/login"
    else:
        return dash.no_update


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
    [Output("confirmation-modal", "style"),
     Output("create-error", "children"),
     Output("create-account-form", "style")],
    [Input("create-account-submit", "n_clicks")],
    [
        State("create-uname-box", "value"),
        State("create-pwd-box", "value"),
        State("confirm-pwd-box", "value"),
        State("create-email-box", "value")
    ]
)
def send_conf(n_clicks, uname, pw, pw_conf, email):
    if n_clicks:
        if pw != pw_conf:
            return {"visibility": "hidden"}, "Passwords don't match!", dash.no_update
        try:
            send_conf_email(email)
        except IntegrityError as exception:
            message = exception.orig.pgerror
            r = re.findall("Key \(email\)=\((.*)\)", message)[0]
            return {"visibility": "hidden"}, f"There's already an account for {r}", dash.no_update
        return {"visibility": "visible"}, dash.no_update, {"opacity": 0.2}
    return dash.no_update, dash.no_update, dash.no_update


@app.callback(
    [Output("url_create", "pathname"), Output("confirm-error", "children")],
    [Input("conf-code-submit", "n_clicks")],
    [
        State("create-uname-box", "value"),
        State("create-pwd-box", "value"),
        State("create-email-box", "value"),
        State("conf-code-box", "value")
    ]
)
def confirm(n_clicks, uname, pwd, email, submitted_code):
    if n_clicks:
        if confirm_code(submitted_code, email):
            add_user(uname, pwd, email)
            return "/login", dash.no_update
        else:
            return dash.no_update, "Wrong Code"
    raise dash.exceptions.PreventUpdate


@app.callback(
        Output("fitbit-heart", "data"),
        [Input("tabs", "value"), Input('url', 'href')]
    )
def load_fitbit_heart_data(tab, url):
    if tab == "fitbit-tab":
        if "access_token" in url:
            return fitbit_heart(get_user_access_token(url))
        raise PreventUpdate
    else:
        raise PreventUpdate

@app.callback(
        Output("fitbit-graph", "figure"),
        [Input("fitbit-heart", "data")]
    )
def graph_fitbit_heart(data):
    print("graphing")
    activities_heart = pd.DataFrame(data["activities-heart"][0]["heartRateZones"])
    heart_intraday = pd.DataFrame(data["activities-heart-intraday"]["dataset"])
    print(heart_intraday)
    heart_intraday_trace = go.Scatter(
        x = heart_intraday["time"],
        y = heart_intraday["value"],
        mode = "lines",
        name = "Heart Rate"
    )
    fig = go.Figure(data = heart_intraday_trace)
    return fig

