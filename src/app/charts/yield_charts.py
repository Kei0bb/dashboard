from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _format_fail_label(column_name: str) -> str:
    if column_name.startswith("FAIL_BIN_"):
        return column_name.replace("FAIL_BIN_", "", 1)
    return column_name


def build_yield_combo_chart(df_summary: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fail_cols = [c for c in df_summary.columns if c.startswith("FAIL_BIN_")]
    x_axis = df_summary["Category"]
    for col in fail_cols:
        fig.add_trace(
            go.Bar(
                x=x_axis,
                y=df_summary[col],
                name=_format_fail_label(col),
            )
        )
    if "0_PASS" in df_summary.columns:
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df_summary["0_PASS"],
                name="Pass Rate",
                mode="lines+markers",
            )
        )
    fig.update_layout(
        barmode="stack",
        title="Yield vs Failure Rate",
        xaxis_title="Period",
        yaxis_title="Rate (%)",
    )
    return fig


def build_distribution_chart(df: pd.DataFrame) -> go.Figure:
    return px.box(
        df,
        x="LotID",
        y="0_PASS",
        color="LotID",
        points="all",
        title="Yield Distribution by Lot",
    )


def build_failure_mode_chart(df: pd.DataFrame) -> go.Figure:
    fail_cols = [c for c in df.columns if c.startswith("FAIL_BIN_")]
    if not fail_cols:
        return go.Figure()
    fail_sum = df[fail_cols].sum().sort_values(ascending=False)
    return px.pie(
        values=fail_sum.values,
        names=[_format_fail_label(name) for name in fail_sum.index],
        title="Failure Mode Contribution",
    )
