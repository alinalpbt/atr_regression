import os
import pandas as pd
from config import *
import signals
import sys
import logging
import fnmatch
import evaluation

'''
主程序，用于执行策略和调用其他模块
'''

# 配置日志记录系统
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError as e:
        logging.error("找不到文件，程序即将退出。")
        sys.exit(1)  # 使用退出代码1标示出错退出

def apply_strategy(df, strategy, params):
    return strategy(df, params)

def main():
    # 通配符匹配所有符合条件的文件
    pattern = "converted_*.csv"
    for file_name in os.listdir(data_path):
        if fnmatch.fnmatch(file_name, pattern):  # 确保文件名匹配给定的模式
            file_path = os.path.join(data_path, file_name)
            df = load_data(file_path)
                
            # 假设所有文件都使用相同的策略
            if df is not None:
                df_processed = apply_strategy(df, signals.ATR_regression, params_list[0])

                # 输出处理后的DataFrame或进行进一步分析的代码
                print(f"处理的文件: {file_name}")
                print(df_processed.head())

                output_file_path = os.path.join(output_path, file_name.replace("converted_", "processed_"))
                df_processed.to_csv(output_file_path, index=False)
                logging.info(f"已处理并保存文件: {output_file_path}")

                # 计算资金曲线、年化收益率、回撤
                position = initial_capital
                evaluation.evaluate_performance(output_file_path)

            else:
                logging.warning(f"Unable to process file: {file_name}")

if __name__ == "__main__":
    main()