import backtrader as bt
import config
from strategy import ATR_Regression_Strategy
from texttable import Texttable 

def run_backtest():
    headers = ["分析项目"]

    for name, data_file in config.data_files: 
        cerebro = bt.Cerebro()
        headers.append(name)

        data = bt.feeds.GenericCSVData( 
            dataname=data_file,
            dtformat='%Y-%m-%d %H:%M:%S%z',
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5
        )
        data._name = name

        # 添加数据、策略
        cerebro.adddata(data, name=name)
        cerebro.addstrategy(ATR_Regression_Strategy)
        
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
        strat = results[0]

        # 获取分析器结果
        returns = strat.analyzers.returns.get_analysis()
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()
        # trades = strat.analyzers.trades.get_analysis()

        # 构建数据表格（始终持仓的策略）
        table = [
            ["分析项目", "结果"],
            ["总收益率", f"{returns['rtot'] * 100:.2f}%" if 'rtot' in returns else "N/A"],
            ["年化收益率", f"{returns['rnorm100']:.2f}%" if 'rnorm100' in returns else "N/A"],
            ["最大回撤", f"{drawdown['max']['drawdown']:.2f}%" if 'max' in drawdown else "N/A"],
            ["夏普比率", f"{sharpe['sharperatio']:.2f}" if 'sharperatio' in sharpe else "N/A"],
            ["总交易笔数", strat.buy_count + strat.sell_count]
        ]

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


        table_output = Texttable()
        table_output.add_rows(table)
        
        print(f"\n{name} 分析结果:")
        print(table_output.draw())

        cerebro.plot(
            style='candlestick',      # 图表样式
            barup='green',            # 上涨柱颜色
            bardown='red',            # 下跌柱颜色
            volup='lightgreen',       # 成交量柱颜色（上涨）
            voldown='pink',           # 成交量柱颜色（下跌）
            tight=True,               # 紧凑布局
            grid=True                 # 显示网格
        )


if __name__ == '__main__':
    run_backtest()