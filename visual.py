import pandas as pd
import plotly.graph_objects as go
import os

# 确保结果目录存在
output_dir = 'data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def plot_results(data, name, strategy_name):
    """
    使用 Plotly 绘制策略结果
    :param data: 包含日期和净值的 DataFrame
    :param name: 数据集名称
    :param strategy_name: 策略名称
    """
    fig = go.Figure()

    # 添加策略收益率
    fig.add_trace(go.Scatter(x=data['date'], y=data['net_value'], mode='lines', name='净值'))

    # 更新布局
    fig.update_layout(
        title=f'{strategy_name} 策略净值 ({name})',
        xaxis_title='日期',
        yaxis_title='净值',
        hovermode='x unified'
    )

    # 输出为 HTML 文件
    fig.write_html(os.path.join(output_dir, f'{name}_{strategy_name}_plot.html'))
    print(f'图表已保存到 {os.path.join(output_dir, f"{name}_{strategy_name}_plot.html")}')
