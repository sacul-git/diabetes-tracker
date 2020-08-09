import dash_core_components as dcc
import dash_html_components as html

from app import app

def serve_layout():
    return html.Div(
            children = [
                dcc.Location(id="url", refresh=False),
                html.Div(
                    className="header",
                    children=[
                        html.Img(
                            className = "logo",
                            src=app.get_asset_url("diabetes.svg")
                        ),
                        html.Span(className="app-title", children="Header Title"),
                        html.Div(
                            id = "header-logout",
                            className = "header-right",
                            children = [
                                html.Span(id = "uname-display"),
                                html.Button(
                                    className="light-button-dark-bg",
                                    id="logout-button",
                                    children = "logout"
                                    )
                                ]
                            )
                        ]
                    ),
                html.Div(
                    className="spacer",
                    children = "good job you found me I'm hiding behind the header"
                ),
                html.Div(id="page-content", className = "page-content"),
                html.Div(
                    className="attribution",
                    children=[
                    "Icons made by ",
                    html.A(href="http://www.freepik.com/", children="Freepick"),
                    " from ",
                    html.A(href="https://www.flaticon.com/", children="flaticon.com")
                    ])
                ],
            )
