import dash_core_components as dcc
import dash_html_components as html

from layouts.fitbit_layout import fitbit_request_auth_layout, fitbit_tab_layout

authenticated_content = html.Div(
        children = [
            html.Div(
                children = [
                    dcc.Tabs(
                        id = "tabs",
                        value = "tracker-tab",
                        children = [
                            dcc.Tab(label = "Tracker", value = "tracker-tab"),
                            dcc.Tab(label = "fitbit data", value = "fitbit-tab")
                            ]
                        ),
                    html.Div(
                        id = "tabs-content",
                        children = [
                        ]
                    )
                ]
            )
        ]
    )
