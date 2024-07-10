# ATR Regression Strategy
仓库为ATR回归策略的实现

## Prerequisites
- 安装 backtrader, matplotlib 库

## 文件目录与用途
config：参数
my_data: 解析数据文件
LTanalyzer：自定义分析器（输出信息，计算数据）
strategy: 自定义策略
main:运行

## 优化方向
# AR可能优化方向：
（杠杆）不要两倍杠杆，1或者1.5倍杠杆
（定投）时间固定，金额不固定，或者固定金额，时间不固定
（滤网）月相/国债利率/ema14 作为因子，投资金额变化
（期权）增加固定收益

# VAD可能优化方向：
（策略）
（可视化）