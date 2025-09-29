import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_summary_chart(
    df_product: pd.DataFrame,
    agg_period: str,
    id_cols: list,
    pass_col: str,
    fail_cols: list,
) -> go.Figure:
    """Creates a combined bar and line chart for yield and failure rates over time or by BulkID."""
    df_product["Time"] = pd.to_datetime(df_product["Time"])

    group_col = "BulkID"
    if agg_period != "BulkID":
        df_product["Period"] = df_product["Time"].dt.to_period(
            {
                "Daily": "D",
                "Weekly": "W",
                "Monthly": "M",
                "Quarterly": "Q",
            }[agg_period]
        )
        group_col = "Period"

    agg_dict = {col: "mean" for col in [pass_col] + fail_cols}
    df_agg = df_product.groupby(group_col).agg(agg_dict).sort_index().reset_index()

    if agg_period == "Weekly":
        x_axis = df_agg[group_col].apply(lambda p: f"{p.start_time.year}-W{p.start_time.weekofyear}").astype(str)
    elif agg_period == "Monthly":
        x_axis = df_agg[group_col].apply(lambda p: p.start_time.strftime('%b')).astype(str)
    else:
        x_axis = df_agg[group_col].astype(str)

    fig_combo = go.Figure()

    for col in fail_cols:
        fig_combo.add_trace(go.Bar(x=x_axis, y=df_agg[col], name=col))

    fig_combo.add_trace(
        go.Scatter(x=x_axis, y=df_agg[pass_col], name="Pass Rate", mode="lines+markers")
    )

    fig_combo.update_layout(
        barmode="stack",
        title=f"Yield and Failure Rate ({agg_period})",
        xaxis_title=agg_period,
        yaxis_title="Rate (%)",
        legend_title="Metrics",
    )
    return fig_combo

def create_yield_distribution_chart(df_product: pd.DataFrame, pass_col: str) -> go.Figure:
    """Creates a box plot showing yield distribution by LotID."""
    fig_box = px.box(
        df_product,
        x="LotID",
        y=pass_col,
        color="LotID",
        points="all",
        title="Yield Distribution by Lot",
    )
    return fig_box

def create_failure_mode_chart(df_product: pd.DataFrame, fail_cols: list) -> go.Figure:
    """Creates a pie chart showing the contribution of different failure modes."""
    if fail_cols:
        fail_sum = df_product[fail_cols].sum().sort_values(ascending=False)
        fig_pie = px.pie(
            fail_sum,
            values=fail_sum.values,
            names=fail_sum.index,
            title="Failure Mode Contribution",
        )
        return fig_pie
    else:
        return go.Figure() # Return an empty figure if no failure columns
