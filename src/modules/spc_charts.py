from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# I-MRチャートの管理限界線計算に使用する定数 (n=2の場合)
D2_CONSTANT = 1.128

def create_wafer_map(df: pd.DataFrame, parameter: str) -> go.Figure:
    """Creates a wafer map for the given parameter."""
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

def load_spec_limits(spec_df: pd.DataFrame, parameter: str) -> tuple[float | None, float | None]:
    """Loads spec limits (USL, LSL) from a spec DataFrame."""

    spec_row = spec_df[spec_df["parameter"] == parameter]

    if spec_row.empty:
        return None, None

    usl = (
        spec_row["USL"].iloc[0]
        if "USL" in spec_row and pd.notna(spec_row["USL"].iloc[0])
        else None
    )
    lsl = (
        spec_row["LSL"].iloc[0]
        if "LSL" in spec_row and pd.notna(spec_row["LSL"].iloc[0])
        else None
    )

    return usl, lsl

def create_individual_chart(df: pd.DataFrame, feature: str, usl: float = None, lsl: float = None):
    """Creates an Individual (I) chart for a given feature."""
    if df.empty or feature not in df.columns:
        return go.Figure()

    individual_values = df[feature]
    cl = individual_values.mean()

    # 移動範囲 (Moving Range) を計算 (n=2)
    moving_ranges = individual_values.diff().abs().dropna()
    avg_moving_range = moving_ranges.mean()

    # 管理限界線 (UCL, LCL) を計算
    # UCL = CL + 3 * (MR_avg / d2)
    # LCL = CL - 3 * (MR_avg / d2)
    ucl = cl + 3 * (avg_moving_range / D2_CONSTANT)
    lcl = cl - 3 * (avg_moving_range / D2_CONSTANT)

    # Iチャートの作成
    fig_i = go.Figure()
    fig_i.add_trace(
        go.Scatter(x=df.index, y=individual_values, mode="lines+markers", name="Individual Value")
    )
    fig_i.add_hline(y=cl, line_dash="dash", annotation_text="CL")
    fig_i.add_hline(y=ucl, line_dash="dot", annotation_text="UCL")
    fig_i.add_hline(y=lcl, line_dash="dot", annotation_text="LCL")

    # 規格限界線 (USL, LSL) を追加
    if usl is not None:
        fig_i.add_hline(y=usl, line_dash="solid", line_color="red", annotation_text="USL")
    if lsl is not None:
        fig_i.add_hline(y=lsl, line_dash="solid", line_color="red", annotation_text="LSL")

    fig_i.update_layout(
        title=f"{feature} Individual Chart",
        xaxis_title="Measurement Point",
        yaxis_title="Value",
    )

    return fig_i
