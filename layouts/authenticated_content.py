import dash_core_components as dcc
import dash_html_components as html

authenticated_content = html.Div(
        children = [
            html.Div(
                children = [
                    dcc.Tabs(
                        id = "tabs",
                        value = "tab1",
                        children = [
                            dcc.Tab(label = "tab1", value = "tab1"),
                            dcc.Tab(label = "tab2", value = "tab2")
                            ]
                        ),
                    html.Div(
                        id = "tabs-content",
                        children = ["This is some content"]
                        )
                    ]
                )
            ]
        )
