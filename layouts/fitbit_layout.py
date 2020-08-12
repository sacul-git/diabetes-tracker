import dash_html_components as html

from utils.fitbit_auth import (
    get_auth_url
)

fitbit_request_auth_layout = html.Div(
    html.A("Login to fitbit", href = get_auth_url())
)

fitbit_tab_layout = html.Div(
    "You're authenticated to fitbit"
)
