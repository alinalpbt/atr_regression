import backtrader as bt
import config
from strategy import ATR_Regression_Strategy, BuyAndHoldStrategy
from texttable import Texttable 
from my_data import MyCSVData
from LTanalyzer import LongTermTradeAnalyzer 
import json
import os

# 确保结果目录存在
output_dir = 'data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
    cerebro.addanalyzer(LongTermTradeAnalyzer, _name='longterm_trades')
    
    # 运行回测
    results = cerebro.run()

    # 获取回测时间
    start_date = data.num2date(data.datetime.array[0]).strftime('%Y-%m-%d')
    end_date = data.num2date(data.datetime.array[-1]).strftime('%Y-%m-%d')

    return results, start_date, end_date

def log_trades(trades, file_name, strategy_name):
    file_path = os.path.join(output_dir, file_name)

    try:
        with open(file_path, 'w') as f:
            if strategy_name == 'ATR_Regression_Strategy':
                f.write("Date,IsBuy,Price,Size,Value,PnL,x,ema200,atr,y,TargetPosition,CurrentPosition\n")  # 写入表头
            else:
                f.write("Date,IsBuy,Price,Size,Value,PnL\n")  # 写入表头
            
            for trade in trades:
                if strategy_name == 'ATR_Regression_Strategy':
                    log_str = f'{trade["date"]},{trade["isbuy"]},{trade["price"]},{trade["size"]},{trade["value"]},{trade["pnl"]},{trade["x"]},{trade["ema200"]},{trade["atr"]},{trade["y"]},{trade["target_position"]},{trade["current_position"]}\n'
                else:
                    log_str = f'{trade["date"]},{trade["isbuy"]},{trade["price"]},{trade["size"]},{trade["value"]},{trade["pnl"]}\n'
                f.write(log_str)
        print(f"Successfully wrote to {file_path}")
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

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
        buy_and_hold_drawdown = buy_and_hold_strat.analyzers.drawdown.get_analysis()

        # 获取 ATR_Regression_Strategy 的分析结果
        atr_regression_returns = atr_regression_strat.analyzers.returns.get_analysis()
        atr_regression_drawdown = atr_regression_strat.analyzers.drawdown.get_analysis()
        atr_regression_sharpe = atr_regression_strat.analyzers.sharpe.get_analysis()

        # 计算超额收益
        excess_returns = atr_regression_returns['rtot'] - buy_and_hold_returns['rtot']

        # 打印回测时间
        print(f"回测时间：从 {start_date} 到 {end_date}")

        buy_and_hold_trades = buy_and_hold_strat.analyzers.longterm_trades.get_analysis()
        atr_regression_trades = atr_regression_strat.analyzers.longterm_trades.get_analysis()

        log_trades(buy_and_hold_trades, f'trades_{name}_buy_and_hold.csv', 'BuyAndHoldStrategy')
        log_trades(atr_regression_trades, f'trades_{name}_atr_regression.csv', 'ATR_Regression_Strategy')

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
            f"{buy_and_hold_drawdown['max']['drawdown']:.2f}%" if 'max' in atr_regression_drawdown else "N/A", 
            " "],
            ["夏普比率", f"{atr_regression_sharpe['sharperatio']:.2f}" if atr_regression_sharpe['sharperatio'] is not None else "N/A",
                         f"{buy_and_hold_sharpe['sharperatio']:.2f}" if buy_and_hold_sharpe['sharperatio'] is not None else "N/A", 
                         " "],
            ["总交易笔数", atr_regression_strat.buy_count + atr_regression_strat.sell_count,
                          buy_and_hold_strat.buy_count + buy_and_hold_strat.sell_count,
                          " "]
        ])

        print(table.draw())

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