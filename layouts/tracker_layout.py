import dash_html_components as html
import dash_core_components as dcc


tracker_tab_layout = html.Div(
    dcc.Graph(id = "tracker-graph")
)
