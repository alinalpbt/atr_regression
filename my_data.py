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
        ('close', 4)
    )

    # 因为我们的数据是非连续的（节假日信息空缺），这里为了减少数据的处理，增加用行数指代bar的位置的逻辑
    def __init__(self, *args, **kwargs):
        super(MyCSVData, self).__init__(*args, **kwargs)
        self.total_lines = 0  # 初始化总行数为0

    def start(self):
        super().start()
        # 打开文件，计算行数
        with open(self.p.dataname, 'r') as f:
            self.total_lines = sum(1 for line in f)

    # 手动解析日期时间信息
    def _loadline(self, linetokens):
        dtfield = linetokens[self.p.datetime]
        dt = datetime.strptime(dtfield, self.p.dtformat)

        # 设置 K 线数据
        self.lines.datetime[0] = bt.date2num(dt)
        self.lines.open[0] = float(linetokens[self.p.open])
        self.lines.high[0] = float(linetokens[self.p.high])
        self.lines.low[0] = float(linetokens[self.p.low])
        self.lines.close[0] = float(linetokens[self.p.close])

        return True
    


