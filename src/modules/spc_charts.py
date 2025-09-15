import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_xbar_r_chart(df: pd.DataFrame, feature: str, subgroup_size: int = 5):
    if df.empty or feature not in df.columns:
        return go.Figure(), go.Figure()

    # サブグループごとの平均と範囲を計算
    # dfはlot_idとsubgroupでソートされていることを前提とする
    subgroup_means = df.groupby('lot_id')[feature].mean()
    subgroup_ranges = df.groupby('lot_id')[feature].apply(lambda x: x.max() - x.min())

    # 全体の平均と平均範囲を計算
    xbar_bar = subgroup_means.mean()
    r_bar = subgroup_ranges.mean()

    # 管理図定数 (n=5の場合)
    A2 = 0.577
    D3 = 0
    D4 = 2.114

    # Xbarチャートの管理限界線
    xbar_ucl = xbar_bar + A2 * r_bar
    xbar_lcl = xbar_bar - A2 * r_bar

    # Rチャートの管理限界線
    r_ucl = D4 * r_bar
    r_lcl = D3 * r_bar

    # Xbarチャートの作成
    fig_xbar = go.Figure()
    fig_xbar.add_trace(go.Scatter(x=subgroup_means.index, y=subgroup_means, mode='lines+markers', name='X-bar'))
    fig_xbar.add_hline(y=xbar_bar, line_dash="dash", annotation_text="CL")
    fig_xbar.add_hline(y=xbar_ucl, line_dash="dot", annotation_text="UCL")
    fig_xbar.add_hline(y=xbar_lcl, line_dash="dot", annotation_text="LCL")
    fig_xbar.update_layout(title=f'{feature} X-bar Chart', xaxis_title="Lot ID", yaxis_title="X-bar")

    # Rチャートの作成
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatter(x=subgroup_ranges.index, y=subgroup_ranges, mode='lines+markers', name='Range'))
    fig_r.add_hline(y=r_bar, line_dash="dash", annotation_text="CL")
    fig_r.add_hline(y=r_ucl, line_dash="dot", annotation_text="UCL")
    fig_r.add_hline(y=r_lcl, line_dash="dot", annotation_text="LCL")
    fig_r.update_layout(title=f'{feature} R Chart', xaxis_title="Lot ID", yaxis_title="Range")

    return fig_xbar, fig_r

def create_individual_chart(df: pd.DataFrame, feature: str, usl: float = None, lsl: float = None):
    if df.empty or feature not in df.columns:
        return go.Figure()

    # 個々の測定値
    individual_values = df[feature]

    # 中心線 (CL) は個々の測定値の平均
    cl = individual_values.mean()

    # 移動範囲 (MR) を計算 (サイズ2)
    moving_ranges = individual_values.diff().abs().dropna()
    avg_moving_range = moving_ranges.mean()

    # 管理図定数 d2 (n=2の場合)
    d2 = 1.128

    # 管理限界線 (UCL, LCL)
    ucl = cl + 3 * (avg_moving_range / d2)
    lcl = cl - 3 * (avg_moving_range / d2)

    # Iチャートの作成
    fig_i = go.Figure()
    fig_i.add_trace(go.Scatter(x=df['lot_id'] + '-' + df['subgroup'].astype(str), y=individual_values, mode='lines+markers', name='Individual Value'))
    fig_i.add_hline(y=cl, line_dash="dash", annotation_text="CL")
    fig_i.add_hline(y=ucl, line_dash="dot", annotation_text="UCL")
    fig_i.add_hline(y=lcl, line_dash="dot", annotation_text="LCL")

    # USLとLSLを追加
    if usl is not None:
        fig_i.add_hline(y=usl, line_dash="solid", line_color="red", annotation_text="USL")
    if lsl is not None:
        fig_i.add_hline(y=lsl, line_dash="solid", line_color="red", annotation_text="LSL")

    fig_i.update_layout(title=f'{feature} Individual Chart', xaxis_title="Lot ID - Subgroup", yaxis_title="Individual Value")

    return fig_i
