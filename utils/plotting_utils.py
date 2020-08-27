import plotly.graph_objects as go

from db_utils import execute_query

q = """
SELECT
       (date || ' ' || time)::timestamp AS data_datetime,
       blood_sugar
FROM
       basic_tracker
WHERE
       blood_sugar IS NOT NULL;
"""

blood_sugar = (
    execute_query(q)
    .sort_values("data_datetime")
)

bs_scatter = go.Scatter(
    x = blood_sugar.data_datetime,
    y = blood_sugar.blood_sugar,
    mode = "lines+markers",
    line_shape = "spline",
    name = "blood_sugar"
    )

target_range = [4.0, 7.0]

target_block = go.Scatter(
    x = [
        blood_sugar.data_datetime.min(),
        blood_sugar.data_datetime.min(),
        blood_sugar.data_datetime.max(),
        blood_sugar.data_datetime.max(),
        blood_sugar.data_datetime.min(),
    ],
    y = [
        target_range[0],
        target_range[1],
        target_range[1],
        target_range[0],
        target_range[0],
    ],
    mode = "lines",
    fill = "toself",
    fillcolor = "rgba(32, 178, 170, 0.5)",
    line = {
        "color" : "RoyalBlue",
        "width" : 0.5
    }
)

fig = go.Figure(
    data = [
        bs_scatter,
        target_block
    ]
)

fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1d",
                     step="day",
                     stepmode="backward"),
                dict(count=4,
                     label="4d",
                     step="day",
                     stepmode="backward"),
                dict(count=7,
                     label="1w",
                     step="day",
                     stepmode="backward"),
                dict(count=2,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date",
        range = [
            pd.to_datetime("today") - pd.Timedelta(days=4),
            pd.to_datetime("today")
        ]
    )
)




fig.write_html("test_data/bs_fig.html")

