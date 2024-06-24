'''
计算资金曲线、年化收益率、回撤等统计指标
'''

def return_drawdown_ratio(equity_curve):
    """
    """

    # ==== 计算年化收益
    annual_return = (equity_curve['equity_curve'].iloc[-1] / equity_curve['equity_curve'].iloc[0]) ** (
        '1 days 00:00:00' / (equity_curve['candle_begin_time'].iloc[-1] - equity_curve['candle_begin_time'].iloc[0]) * 365) - 1

    # ==== 计算最大回撤
    # 计算当日之前的资金曲线的最高点
    equity_curve['max2here'] = equity_curve['equity_curve'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    equity_curve['dd2here'] = equity_curve['equity_curve'] / equity_curve['max2here'] - 1
    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(equity_curve.sort_values(by=['dd2here']).iloc[0][['candle_begin_time', 'dd2here']])

    # ==== 年化收益/回撤比
    if max_draw_down == 0:
        MAR = 0
    else:
        MAR = annual_return / abs(max_draw_down)

    return annual_return, max_draw_down, MAR