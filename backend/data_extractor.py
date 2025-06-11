#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热水系统数据提取程序
功能：从Excel文件中提取热水流量数据，转换为指定的CSV格式
作者：AI Assistant
日期：2025年
"""

import pandas as pd
import re
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_water_flow_data(excel_file_path, output_dir='.'):
    """
    从Excel文件中提取热水流量数据并转换为CSV格式
    
    Args:
        excel_file_path (str): Excel文件路径
        output_dir (str): 输出目录，默认为当前目录
    
    Returns:
        bool: 处理是否成功
    """
    try:
        logger.info(f"开始处理Excel文件: {excel_file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(excel_file_path):
            logger.error(f"文件不存在: {excel_file_path}")
            return False
        
        # 读取所有sheet
        logger.info("正在读取Excel文件的所有工作表...")
        sheets = pd.read_excel(excel_file_path, sheet_name=None, header=None, dtype=str)
        logger.info(f"共找到 {len(sheets)} 个工作表")
        
        all_final_rows = []
        
        # 处理每个工作表
        for sheet_name, raw_df in sheets.items():
            logger.info(f"正在处理工作表: {sheet_name}")
            final_rows = process_sheet(raw_df, sheet_name)
            all_final_rows.extend(final_rows)
            logger.info(f"工作表 {sheet_name} 处理完成，提取了 {len(final_rows)} 条记录")
        
        if not all_final_rows:
            logger.warning("没有提取到任何数据")
            return False
        
        # 构建DataFrame并处理数据
        logger.info("正在构建最终数据集...")
        final_df = build_final_dataframe(all_final_rows)
        
        # 按楼栋分别导出CSV文件
        export_csv_by_building(final_df, output_dir)
        
        logger.info("数据提取和转换完成！")
        return True
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}")
        return False

def process_sheet(raw_df, sheet_name):
    """
    处理单个工作表的数据
    
    Args:
        raw_df (DataFrame): 原始数据框
        sheet_name (str): 工作表名称
    
    Returns:
        list: 处理后的数据行列表
    """
    final_rows = []
    current_date = None
    current_weekday = None
    header_map = []
    
    for idx, row in raw_df.iterrows():
        try:
            # 处理标题行（如2025/4/1(星期一）...）
            if isinstance(row.iloc[0], str) and re.match(r'\d{4}/\d{1,2}/\d{1,2}\(星期[一二三四五六日1234567]', row.iloc[0]):
                current_date, current_weekday, header_map = parse_header_row(row)
                continue
            
            # 跳过合计行
            if isinstance(row.iloc[0], str) and '合计' in row.iloc[0]:
                continue
            
            # 处理数据行（时间段开头）
            if isinstance(row.iloc[0], str) and re.match(r'\d{2}:\d{2}-\d{2}:\d{2}', row.iloc[0]):
                data_rows = parse_data_row(row, current_date, current_weekday, header_map)
                final_rows.extend(data_rows)
                
        except Exception as e:
            logger.warning(f"处理第 {idx} 行时发生错误: {str(e)}")
            continue
    
    return final_rows

def parse_header_row(row):
    """
    解析标题行，提取日期、星期和楼栋信息
    
    Args:
        row: 数据行
    
    Returns:
        tuple: (日期, 星期, 楼栋映射)
    """
    match = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})\(星期([一二三四五六日1234567])', row.iloc[0])
    if not match:
        return None, None, []
    
    year, month, day, weekday = match.groups()
    current_date = f'{year}-{int(month):02d}-{int(day):02d}'
    
    # 星期映射
    week_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7
    }
    current_weekday = week_map.get(weekday, 0)
    
    # 解析楼栋信息 - 更全面的搜索
    header_map = []
    logger.info(f"正在解析日期 {current_date} 的标题行，共 {len(row)} 列")
    
    # 打印所有列的内容以便调试
    for i in range(len(row)):
        cell_value = row.iloc[i]
        if cell_value and str(cell_value).strip():
            logger.debug(f"列 {i}: '{cell_value}'")
    
    # 检查所有列，寻找包含'栋'或'校外'的字符串
    for i in range(len(row)):
        cell_value = row.iloc[i]
        if isinstance(cell_value, str) and ('栋' in cell_value or '校外' in cell_value):
            building = cell_value.strip()
            # 确保这是一个有效的楼栋名称
            if building and not building.startswith('合计'):
                header_map.append((i, building))
                logger.info(f"发现楼栋: {building} (列索引: {i})")
        elif cell_value and isinstance(cell_value, (int, float)):
            # 检查数字类型的单元格
            cell_str = str(cell_value).strip()
            if '栋' in cell_str:
                match_num = re.search(r'\d+栋', cell_str)
                if match_num:
                    building = f"校内{match_num.group()}"
                    header_map.append((i, building))
                    logger.info(f"发现楼栋: {building} (列索引: {i})")
            elif '校外' in cell_str:
                match_num = re.search(r'校外\d+', cell_str)
                if match_num:
                    building = match_num.group()
                    header_map.append((i, building))
                    logger.info(f"发现楼栋: {building} (列索引: {i})")
    
    # 如果没有找到楼栋，尝试更宽松的匹配
    if not header_map:
        logger.warning(f"使用严格匹配未找到楼栋，尝试宽松匹配...")
        for i in range(len(row)):
            cell_value = row.iloc[i]
            if cell_value:
                cell_str = str(cell_value).strip()
                # 匹配数字+栋的模式
                if re.search(r'\d+栋', cell_str):
                    building = cell_str if isinstance(cell_value, str) else f"校内{re.search(r'\d+栋', cell_str).group()}"
                    header_map.append((i, building))
                    logger.info(f"宽松匹配发现楼栋: {building} (列索引: {i})")
                # 匹配校外楼栋
                elif re.search(r'校外\d+', cell_str):
                    building = re.search(r'校外\d+', cell_str).group()
                    header_map.append((i, building))
                    logger.info(f"宽松匹配发现楼栋: {building} (列索引: {i})")
    
    logger.info(f"共发现 {len(header_map)} 个楼栋: {[building for _, building in header_map]}")
    return current_date, current_weekday, header_map

def parse_data_row(row, current_date, current_weekday, header_map):
    """
    解析数据行，提取时间和流量信息
    
    Args:
        row: 数据行
        current_date: 当前日期
        current_weekday: 当前星期
        header_map: 楼栋映射
    
    Returns:
        list: 数据记录列表
    """
    if not current_date or not header_map:
        return []
    
    time_str = row.iloc[0]
    hour = int(time_str[:2])
    
    data_rows = []
    for idx_b, building in header_map:
        try:
            # 智能查找水流量数据
            # 尝试在楼栋列及其附近列查找数值数据
            flow = 0.0
            money = 0.0
            
            # 检查楼栋列本身
            if idx_b < len(row):
                try:
                    flow = float(row.iloc[idx_b]) if row.iloc[idx_b] not in [None, '', 'nan', building] else 0.0
                except:
                    flow = 0.0
            
            # 如果楼栋列没有数值，检查相邻列
            if flow == 0.0:
                # 检查楼栋列前一列（可能是金额）
                if idx_b > 0:
                    try:
                        money = float(row.iloc[idx_b - 1]) if row.iloc[idx_b - 1] not in [None, '', 'nan'] else 0.0
                    except:
                        money = 0.0
                
                # 检查楼栋列后一列（可能是流量）
                if idx_b + 1 < len(row):
                    try:
                        flow = float(row.iloc[idx_b + 1]) if row.iloc[idx_b + 1] not in [None, '', 'nan'] else 0.0
                    except:
                        flow = 0.0
                
                # 如果后一列也没有，再检查后两列
                if flow == 0.0 and idx_b + 2 < len(row):
                    try:
                        flow = float(row.iloc[idx_b + 2]) if row.iloc[idx_b + 2] not in [None, '', 'nan'] else 0.0
                    except:
                        flow = 0.0
            
            data_rows.append({
                '日期': current_date,
                '星期': current_weekday,
                '小时': hour,
                '金额': round(money, 3),
                '水流量': round(flow, 3),
                '楼栋': building
            })
            
        except Exception as e:
            logger.warning(f"解析楼栋 {building} 数据时发生错误: {str(e)}")
            # 添加默认记录
            data_rows.append({
                '日期': current_date,
                '星期': current_weekday,
                '小时': hour,
                '金额': 0.0,
                '水流量': 0.0,
                '楼栋': building
            })
    
    return data_rows

def build_final_dataframe(all_final_rows):
    """
    构建最终的数据框并计算滞后特征
    
    Args:
        all_final_rows (list): 所有数据行
    
    Returns:
        DataFrame: 处理后的数据框
    """
    # 构建DataFrame
    final_df = pd.DataFrame(all_final_rows)
    
    # 处理日期、星期、小时
    final_df['日期'] = pd.to_datetime(final_df['日期'], errors='coerce')
    final_df['星期'] = final_df['星期'].fillna(0).astype(int)
    final_df['小时'] = final_df['小时'].astype(int)
    final_df['金额'] = final_df['金额'].fillna(0).round(3)
    final_df['水流量'] = final_df['水流量'].round(3)
    
    # 按楼栋、日期、小时排序，方便计算滞后特征
    final_df = final_df.sort_values(by=['楼栋', '日期', '小时']).reset_index(drop=True)
    
    # 计算前一天和前一周的水流量
    logger.info("正在计算前一天和前一周的水流量...")
    final_df['前一天水流量'] = final_df.groupby('楼栋')['水流量'].shift(24)
    final_df['前一周水流量'] = final_df.groupby('楼栋')['水流量'].shift(24 * 7)
    
    # 填充没有滞后数据的行，使用当前水流量值
    final_df['前一天水流量'] = final_df['前一天水流量'].fillna(final_df['水流量']).round(3)
    final_df['前一周水流量'] = final_df['前一周水流量'].fillna(final_df['水流量']).round(3)
    
    return final_df

def export_csv_by_building(final_df, output_dir):
    """
    按楼栋分别导出CSV文件
    
    Args:
        final_df (DataFrame): 最终数据框
        output_dir (str): 输出目录
    """
    logger.info("正在按楼栋导出CSV文件...")
    
    for building in final_df['楼栋'].unique():
        try:
            # 筛选当前楼栋的数据
            building_df = final_df[final_df['楼栋'] == building].copy()
            
            # 选择需要的列并重命名以匹配目标格式
            out_df = building_df[['日期', '星期', '小时', '水流量', '前一天水流量', '前一周水流量']].copy()
            out_df.columns = ['日期', '星期', '小时', '用水量', '前一天用水量', '前一周用水量']
            
            # 日期转为数值格式（如20240401）
            out_df['日期'] = out_df['日期'].dt.strftime('%Y%m%d').astype(int)
            
            # 导出CSV文件
            output_file = os.path.join(output_dir, f'{building}.csv')
            out_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            logger.info(f"已导出 {building} 的数据到 {output_file}，共 {len(out_df)} 条记录")
            
        except Exception as e:
            logger.error(f"导出 {building} 数据时发生错误: {str(e)}")

def main():
    """
    主函数
    """
    # Excel文件路径
    excel_file = '2025年2月起热水流量.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        logger.error(f"Excel文件不存在: {excel_file}")
        logger.info("请确保Excel文件在当前目录下")
        return
    
    # 执行数据提取
    success = extract_water_flow_data(excel_file)
    
    if success:
        logger.info("数据提取完成！生成的CSV文件格式为：日期,星期,小时,用水量,前一天用水量,前一周用水量")
    else:
        logger.error("数据提取失败，请检查日志信息")

if __name__ == '__main__':
    main()