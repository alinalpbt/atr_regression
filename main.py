import backtrader as bt
import config
from strategy import ATR_Regression_Strategy, BuyAndHoldStrategy
from texttable import Texttable 
from my_data import MyCSVData
    
def add_data_and_run_strategy(strategy_class, data_file, name):
    cerebro = bt.Cerebro()
    data = MyCSVData(  # 使用自定义数据源类
        dataname=data_file,
        dtformat='%Y/%m/%d %H:%M',
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5
    )
    
    # 添加数据、策略
    cerebro.adddata(data, name=name)
    cerebro.addstrategy(strategy_class) # 动态添加策略

    # 添加资金、佣金、滑点
    cerebro.broker.setcash(config.initial_cash)
    cerebro.broker.setcommission(commission=config.commission_rate)
    cerebro.broker.set_slippage_perc(perc=config.slippage)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # 运行回测
    results = cerebro.run()

    # 获取回测时间
    start_date = data.num2date(data.datetime.array[0]).strftime('%Y-%m-%d')
    end_date = data.num2date(data.datetime.array[-1]).strftime('%Y-%m-%d')

    return results, start_date, end_date

def calculate_max_drawdown(equity_curve):
    max_drawdown = 0
    peak = max(equity_curve)
    trough = min(equity_curve)
    max_drawdown = (peak - trough) / peak * 100
    return max_drawdown

def run_backtest():
    for name, data_file in config.data_files:
        print(f"\n{name} 分析结果:")

        # 运行 BuyAndHoldStrategy 策略
        buy_and_hold_results, start_date, end_date = add_data_and_run_strategy(BuyAndHoldStrategy, data_file, name)
        buy_and_hold_strat = buy_and_hold_results[0]

        # 运行 ATR_Regression_Strategy 策略
        atr_regression_results, _, _ = add_data_and_run_strategy(ATR_Regression_Strategy, data_file, name)
        atr_regression_strat = atr_regression_results[0]

        # 获取 BuyAndHoldStrategy 的分析结果
        buy_and_hold_returns = buy_and_hold_strat.analyzers.returns.get_analysis()
        buy_and_hold_sharpe = buy_and_hold_strat.analyzers.sharpe.get_analysis()

        # 获取 ATR_Regression_Strategy 的分析结果
        atr_regression_returns = atr_regression_strat.analyzers.returns.get_analysis()
        atr_regression_drawdown = atr_regression_strat.analyzers.drawdown.get_analysis()
        atr_regression_sharpe = atr_regression_strat.analyzers.sharpe.get_analysis()

        # 计算超额收益
        excess_returns = atr_regression_returns['rtot'] - buy_and_hold_returns['rtot']

        # 获取 BuyAndHoldStrategy 的权益曲线
        equity_curve = buy_and_hold_strat.equity_curve
        buy_and_hold_max_drawdown = calculate_max_drawdown(equity_curve)

        # 打印回测时间
        print(f"回测时间：从 {start_date} 到 {end_date}")

        # 构建数据表格
        table = Texttable()
        table.add_rows([
            ["分析项目", "ATR_Regression", "BuyAndHold", "超额收益"],
            ["总收益率", f"{atr_regression_returns['rtot'] * 100:.2f}%" if 'rtot' in atr_regression_returns else "N/A",
                            f"{buy_and_hold_returns['rtot'] * 100:.2f}%" if 'rtot' in buy_and_hold_returns else "N/A",
                            f"{excess_returns * 100:.2f}%" if excess_returns else "N/A"],
            ["年化收益率", f"{atr_regression_returns['rnorm100']:.2f}%" if 'rnorm100' in atr_regression_returns else "N/A",
                            f"{buy_and_hold_returns['rnorm100']:.2f}%" if 'rnorm100' in buy_and_hold_returns else "N/A", 
                            " "],
            ["最大回撤", f"{atr_regression_drawdown['max']['drawdown']:.2f}%" if 'max' in atr_regression_drawdown else "N/A",
                            f"{buy_and_hold_max_drawdown:.2f}%" if buy_and_hold_max_drawdown is not None else "N/A", 
                            " "],
            ["夏普比率", f"{atr_regression_sharpe['sharperatio']:.2f}" if atr_regression_sharpe['sharperatio'] is not None else "N/A",
                         f"{buy_and_hold_sharpe['sharperatio']:.2f}" if buy_and_hold_sharpe['sharperatio'] is not None else "N/A", 
                         " "],
            ["总交易笔数", atr_regression_strat.buy_count + atr_regression_strat.sell_count,
                          buy_and_hold_strat.buy_count + buy_and_hold_strat.sell_count,
                          " "]
        ])

        print(table.draw())

            # # 构建数据表格（CTA的策略）
            # table = [
            #     ["分析项目", "结果"],
            #     ["总收益率", f"{returns['rtot'] * 100:.2f}%" if 'rtot' in returns else "N/A"],
            #     ["年化收益率", f"{returns['rnorm100']:.2f}%" if 'rnorm100' in returns else "N/A"],
            #     ["最大回撤", f"{drawdown['max']['drawdown']:.2f}%" if 'max' in drawdown else "N/A"],
            #     ["夏普比率", f"{sharpe['sharperatio']:.2f}" if 'sharperatio' in sharpe else "N/A"],
            #     ["总交易笔数", trades.total]
            #     ["总关闭交易数", trades.total.closed if hasattr(trades.total, 'closed') else "N/A"],
            #     ["总盈利交易数", trades.won.total if hasattr(trades.won, 'total') else "N/A"],
            #     ["总亏损交易数", trades.lost.total if hasattr(trades.lost, 'total') else "N/A"],
            #     ["平均每笔盈利", f"{trades.won.pnl.average:.2f}" if hasattr(trades.won.pnl, 'average') else "N/A"],
            #     ["平均每笔亏损", f"{trades.lost.pnl.average:.2f}" if hasattr(trades.lost.pnl, 'average') else "N/A"],
            #     ["最长连续盈利交易数", trades.streak.won.longest if hasattr(trades.streak.won, 'longest') else "N/A"],
            #     ["最长连续亏损交易数", trades.streak.lost.longest if hasattr(trades.streak.lost, 'longest') else "N/A"]
            # ]

            # cerebro.plot(
            #     style='candlestick',      # 图表样式
            #     barup='green',            # 上涨柱颜色
            #     bardown='red',            # 下跌柱颜色
            #     volup='lightgreen',       # 成交量柱颜色（上涨）
            #     voldown='pink',           # 成交量柱颜色（下跌）
            #     tight=True,               # 紧凑布局
            #     grid=True                 # 显示网格
            # )


if __name__ == '__main__':
    run_backtest()