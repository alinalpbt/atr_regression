import backtrader as bt
from datetime import datetime

'''
大聪明backtrader解析不了4h bar，所以手动解析了
'''

class MyCSVData(bt.feeds.GenericCSVData):
    params = (
        ('dtformat', '%Y/%m/%d %H:%M'),
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
    )

    def _loadline(self, linetokens):
        # 手动解析日期时间信息
        dtfield = linetokens[self.p.datetime]
        dt = datetime.strptime(dtfield, self.p.dtformat)

        # 设置 K 线数据
        self.lines.datetime[0] = bt.date2num(dt)
        self.lines.open[0] = float(linetokens[self.p.open])
        self.lines.high[0] = float(linetokens[self.p.high])
        self.lines.low[0] = float(linetokens[self.p.low])
        self.lines.close[0] = float(linetokens[self.p.close])
        self.lines.volume[0] = float(linetokens[self.p.volume])

        return True