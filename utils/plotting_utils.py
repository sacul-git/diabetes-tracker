import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from db_utils import execute_query

def get_basic_data(schema: str) -> pd.DataFrame:
    """
    Get the basic tracker data from the specified schema

    Arguments:
        - schema (str): the schema containing the basic_tracker table from
          where the data are to be pulled

    Returns:
        pd.DataFrame containing the data
    """
    q = f"""
        SELECT
                   (date || ' ' || time)::timestamp AS data_datetime,
                   insulin_injection_basal_units,
                   insulin_meal,
                   meal_carbohydrates,
                   blood_sugar
         FROM
                   {schema}.basic_tracker
    """
    data = (
        execute_query(q)
        .sort_values("data_datetime")
    )
    return data

def create_bs_fig(data: pd.DataFrame) -> go.Figure:
    """
    Makes the main blood sugar dataframe from the mySugr export data

    Arguments:
        - data (pd.DataFrame): needs to contain the following columns:
            - data_datetime (timestamp)
            - insulin_injection_basal_units (float)
            - insulin_meal (float)
            - meal_carbohidrates (float)
            - blood_sugar (float)

    Returns:
        plotly.graph_objects._figure.Figure
    """
    blood_sugar = data.loc[data.blood_sugar.notnull()]
    bs_scatter = go.Scatter(
        x = blood_sugar.data_datetime,
        y = blood_sugar.blood_sugar,
        mode = "lines+markers",
        line_shape = "spline",
        name = "Blood Sugar",
        yaxis = "y1",
        marker = {
            "color" : "#5D8CAE"
            }
        )
    ins_meal = data.loc[data.insulin_meal.notnull()]
    fast_insulin_bars = go.Bar(
        x = ins_meal.data_datetime,
        y = ins_meal.insulin_meal,
        name = "Fast Insulin Units",
        yaxis = "y2",
        opacity = 0.25,
        # one hour width:
        width = 1000 * 3600,
        marker = {
            "color": "#48D1CC"
            }
    )
    ins_basal = data.loc[data.insulin_injection_basal_units.notnull()]
    basal_insulin_bars = go.Bar(
        x = ins_basal.data_datetime,
        y = ins_basal.insulin_injection_basal_units,
        name = "Basal Insulin Units",
        yaxis = "y2",
        opacity = 0.25,
        # one hour width:
        width = 1000 * 3600,
        marker = {
            "color": "#5F9EA0"
            }
    )
    carbs = data.loc[data.meal_carbohydrates.notnull()]
    carb_bars = go.Bar(
        x = carbs.data_datetime,
        y = carbs.meal_carbohydrates,
        name = "Carbs",
        yaxis = "y3",
        opacity = 0.25,
        # one hour width:
        width = 1000 * 3600,
        marker = {
            "color": "#B22222"
            }
    )
    target_range = [4.0, 7.0]
    target_block = go.Scatter(
        x = [
            data.data_datetime.min(),
            data.data_datetime.min(),
            data.data_datetime.max(),
            data.data_datetime.max(),
            data.data_datetime.min(),
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
        fillcolor = "rgba(32, 178, 170, 0.25)",
        line = {
            "color" : "RoyalBlue",
            "width" : 0.5
        },
        yaxis = "y1",
        name = "Blood Sugar Target Zone"
    )
    # Create figure and add traces:
    fig = go.Figure()
    fig.add_trace(target_block)
    fig.add_trace(fast_insulin_bars)
    fig.add_trace(basal_insulin_bars)
    fig.add_trace(bs_scatter)
    fig.add_trace(carb_bars)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            domain = [0.05, 1],
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
        ),
        yaxis={
            "title": "Blood Sugar (mmol/mg)",
        },
        yaxis2={
            "title": "Inuslin Units",
            "anchor": "x",
            "overlaying":"y",
            "side":"right",
        },
        yaxis3={
            "title":"Carbs",
            "anchor":"free",
            "overlaying":"y",
        },
    )
    return fig
