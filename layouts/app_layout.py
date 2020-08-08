import dash_core_components as dcc
import dash_html_components as html

def serve_layout():
    return html.Div(
            children = [
                dcc.Location(id="url", refresh=False),
                html.Div(
                    className="header",
                    children=[
                        html.H1("Header Title"),
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
                html.Div(id="page-content", className = "below-header")
                ]
            )
