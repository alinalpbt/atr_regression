import pandas as pd
import os

# 输入目录和输出目录
input_dir = 'original'
output_dir = 'results'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 获取 input_dir 目录中的所有 CSV 文件
file_paths = [os.path.join(input_dir, file) for file in os.listdir(input_dir) if file.endswith('.csv')]

# 处理每个文件
for file_path in file_paths:
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 将时间列从时间戳转换为UTC的年月日时分格式
    df['time'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.strftime('%Y/%m/%d %H:%M')

    # 生成输出文件路径
    base_name = os.path.basename(file_path)
    output_path = os.path.join(output_dir, f'{base_name}')

    # 保存转换后的结果到新的CSV文件，不包括volume列
    df.drop(columns=['volume'], errors='ignore', inplace=True)  # 忽略不存在的列
    df.to_csv(output_path, index=False)

    # 保存转换后的结果到新的CSV文件
    df.to_csv(output_path, index=False)

    print(f"时间格式转换完成，已保存到 {output_path}")

print("所有文件的时间格式转换完成。")
