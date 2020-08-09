import dash_html_components as html
import dash_core_components as dcc

login_layout = html.Div(
    children=[
        dcc.Loading(
            html.Div(
                className="login-logout",
                children=[
                    dcc.Location(id="url_login", refresh=True),
                    html.H1("Sign in"),
                    html.Div(
                        className="login-input",
                        children=[
                            dcc.Input(
                                placeholder="Username",
                                type="text",
                                id="uname-box",
                                debounce=True
                            ),
                            dcc.Input(
                                placeholder="password",
                                type="password",
                                id="pwd-box",
                                debounce=True
                            ),
                            html.Button(
                                children="Go",
                                n_clicks=0,
                                type="submit",
                                id="login-button",
                                className="a-button"
                            ),
                            html.Div(
                                children='',
                                id="login-error",
                                className="error-message"
                            )
                        ]
                    ),
                    html.Div(
                        className="footer",
                        children=[
                            html.Button(
                                children="Create Account",
                                n_clicks=0,
                                type="submit",
                                id="create-account-button",
                                className="a-button"
                            )
                        ]
                    )
                ]
            ),
            type="graph"
        )
    ]
)

logout_layout = html.Div(
    children=[
        html.Div(
            className="login-logout",
            children=[
                dcc.Location(id="url_logout", refresh=True),
                html.H3("You're Logged Out"),
                html.Div(
                    children=[
                        html.Button(
                            children="Back to Login",
                            n_clicks=0,
                            type="submit",
                            id="re-login-button",
                            className="a-button"
                        )
                    ]
                ),
            ]
        )
    ]
)

create_account_layout = html.Div(
    children=[

        html.Div(
            className="modal login-input",
            id="confirmation-modal",
            children=[
                dcc.Input(
                    placeholder="Confirmation Code (check ur email)",
                    type="text",
                    id="conf-code-box",
                    debounce=True
                ),
                html.Button(
                    children="Go",
                    n_clicks=0,
                    type="submit",
                    id="conf-code-submit",
                    className="a-button"
                ),
                html.Div(
                    children='',
                    id="confirm-error",
                    className="error-message"
                )
            ]
        ),
        dcc.Loading(
            html.Div(
                className="login-logout",
                id = "create-account-form",
                children=[
                    dcc.Location(id="url_create", refresh=True),
                    html.H1("Create an Account"),
                    html.Div(
                        className="login-input",
                        children=[
                            dcc.Input(
                                placeholder="Username",
                                type="text",
                                id="create-uname-box",
                                debounce=True
                            ),
                            dcc.Input(
                                placeholder="Password",
                                type="password",
                                id="create-pwd-box",
                                debounce=True
                            ),
                            dcc.Input(
                                placeholder="Confirm Password",
                                type="password",
                                id="confirm-pwd-box",
                                debounce=True
                            ),
                            dcc.Input(
                                placeholder="Email",
                                type="text",
                                id="create-email-box",
                                debounce=True
                            ),
                            html.Button(
                                children="Go",
                                n_clicks=0,
                                type="submit",
                                id="create-account-submit",
                                className="a-button"
                            ),
                            html.Div(
                                children='',
                                id="create-error",
                                className="error-message"
                            )
                        ]
                    ),
                ],
            ),
            type="graph"
        )
    ]
)
