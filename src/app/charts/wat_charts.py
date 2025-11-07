from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


D2_CONSTANT = 1.128


def build_bulk_trend_chart(df_trend: pd.DataFrame, parameter: str, usl: float | None, lsl: float | None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_trend["BulkID"],
            y=df_trend["mean_val"],
            name="Bulk Mean",
            mode="markers",
            marker=dict(size=6),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_trend["BulkID"],
            y=df_trend["moving_avg"],
            name="Moving Avg (n=3)",
            mode="lines",
            line=dict(color="red", width=2),
        )
    )
    if usl is not None:
        fig.add_hline(y=usl, line_dash="dash", line_color="orange", annotation_text="USL")
    if lsl is not None:
        fig.add_hline(y=lsl, line_dash="dash", line_color="orange", annotation_text="LSL")
    fig.update_layout(
        title=f"{parameter} Trend by Bulk",
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


def build_wafer_map(df: pd.DataFrame, parameter: str) -> go.Figure:
    if (
        df.empty
        or parameter not in df.columns
        or "DieX" not in df.columns
        or "DieY" not in df.columns
    ):
        return go.Figure()
    fig = go.Figure(
        go.Heatmap(
            x=df["DieX"],
            y=df["DieY"],
            z=df[parameter],
            colorscale="Viridis",
            showscale=True,
        )
    )
    fig.update_layout(
        title=f"Wafer Map: {parameter}",
        xaxis_title="Die X",
        yaxis_title="Die Y",
        yaxis_scaleanchor="x",
    )
    return fig


def build_individual_chart(df: pd.DataFrame, parameter: str, usl: float | None, lsl: float | None) -> go.Figure:
    if df.empty or parameter not in df.columns:
        return go.Figure()

    values = df[parameter]
    cl = values.mean()
    moving_ranges = values.diff().abs().dropna()
    avg_mr = moving_ranges.mean() if not moving_ranges.empty else 0
    ucl = cl + 3 * (avg_mr / D2_CONSTANT) if avg_mr else cl
    lcl = cl - 3 * (avg_mr / D2_CONSTANT) if avg_mr else cl

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=values, mode="lines+markers", name="Value"))
    fig.add_hline(y=cl, line_dash="dash", annotation_text="CL")
    fig.add_hline(y=ucl, line_dash="dot", annotation_text="UCL")
    fig.add_hline(y=lcl, line_dash="dot", annotation_text="LCL")
    if usl is not None:
        fig.add_hline(y=usl, line_dash="solid", line_color="red", annotation_text="USL")
    if lsl is not None:
        fig.add_hline(y=lsl, line_dash="solid", line_color="red", annotation_text="LSL")
    fig.update_layout(title=f"{parameter} Individual Chart")
    return fig
