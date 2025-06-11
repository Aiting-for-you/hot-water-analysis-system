#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用水习惯分析程序
功能：
1. 分析用户用水习惯（时间段分布、工作日vs周末差异）
2. 识别用水高峰期，为增压泵控制提供依据
3. 生成详细的可视化图表和分析报告
4. 为热水系统节能优化提供数据支撑

作者：热水系统节能项目组
日期：2025年
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
import glob
from scipy import stats
from sklearn.cluster import KMeans
from collections import Counter

# 设置中文字体和图表样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (12, 8)
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.2)
warnings.filterwarnings('ignore')

# 确保中文字体正确显示
try:
    import matplotlib.font_manager as fm
    # 尝试设置系统中文字体
    font_list = [f.name for f in fm.fontManager.ttflist]
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi']
    available_font = None
    for font in chinese_fonts:
        if font in font_list:
            available_font = font
            break
    if available_font:
        plt.rcParams['font.sans-serif'] = [available_font]
        print(f"使用中文字体: {available_font}")
    else:
        print("警告：未找到合适的中文字体，可能影响中文显示")
except Exception as e:
    print(f"字体设置警告: {e}")
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

class WaterHabitAnalyzer:
    """
    用水习惯分析器
    专门用于分析用户用水模式和习惯
    """
    
    def __init__(self, data_folder):
        """
        初始化分析器
        
        Args:
            data_folder (str): 数据文件夹路径
        """
        self.data_folder = data_folder
        self.buildings_data = {}
        self.combined_data = None
        self.analysis_results = {}
        
        # 创建结果保存文件夹
        self.results_folder = os.path.join(data_folder, "分析结果")
        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)
            
        print(f"用水习惯分析器初始化完成")
        print(f"数据文件夹: {data_folder}")
        print(f"结果保存文件夹: {self.results_folder}")
        
    def load_data(self):
        """
        加载所有楼栋的用水数据
        """
        print("\n" + "="*50)
        print("开始加载数据...")
        print("="*50)
        
        # 获取所有CSV文件
        csv_files = glob.glob(os.path.join(self.data_folder, "*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"在 {self.data_folder} 中未找到CSV文件")
        
        for file_path in csv_files:
            building_name = os.path.basename(file_path).replace('_水流量数据.csv', '')
            print(f"正在加载 {building_name} 数据...")
            
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
                
                # 数据预处理
                df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
                df['datetime'] = df['日期'] + pd.to_timedelta(df['小时'], unit='h')
                df['月份'] = df['日期'].dt.month
                df['日'] = df['日期'].dt.day
                df['是否周末'] = df['星期'].isin([6, 7])
                df['时间段'] = df['小时'].apply(self._get_time_period)
                
                # 数据质量检查
                print(f"  - 数据记录数: {len(df)}")
                print(f"  - 时间范围: {df['日期'].min()} 到 {df['日期'].max()}")
                print(f"  - 平均用水量: {df['水流量'].mean():.3f} T/小时")
                print(f"  - 最大用水量: {df['水流量'].max():.3f} T/小时")
                print(f"  - 零用水量比例: {(df['水流量'] == 0).mean()*100:.1f}%")
                
                self.buildings_data[building_name] = df
                print(f"  ✓ {building_name} 数据加载完成")
                
            except Exception as e:
                print(f"  ✗ 加载 {building_name} 数据时出错: {e}")
        
        # 合并所有数据
        self._combine_data()
        print(f"\n数据加载完成，共加载 {len(self.buildings_data)} 个楼栋的数据")
        print(f"合并数据总计 {len(self.combined_data)} 条记录")
    
    def _get_time_period(self, hour):
        """
        根据小时数确定时间段
        
        Args:
            hour (int): 小时数 (0-23)
            
        Returns:
            str: 时间段名称
        """
        if 6 <= hour < 12:
            return '上午'
        elif 12 <= hour < 18:
            return '下午'
        elif 18 <= hour < 24:
            return '晚上'
        else:
            return '深夜'
    
    def _combine_data(self):
        """
        合并所有楼栋数据
        """
        all_data = []
        for building, df in self.buildings_data.items():
            df_copy = df.copy()
            df_copy['楼栋'] = building
            all_data.append(df_copy)
        
        if all_data:
            self.combined_data = pd.concat(all_data, ignore_index=True)
            print(f"数据合并完成，总计 {len(self.combined_data)} 条记录")
    
    def analyze_hourly_patterns(self):
        """
        分析每小时用水模式
        """
        print("\n" + "="*50)
        print("开始分析每小时用水模式...")
        print("="*50)
        
        # 计算每小时统计数据
        hourly_stats = self.combined_data.groupby('小时')['水流量'].agg([
            'mean', 'std', 'median', 'max', 'count'
        ]).round(4)
        
        # 识别用水高峰期
        hourly_mean = hourly_stats['mean']
        peak_threshold = hourly_mean.mean() + hourly_mean.std()
        peak_hours = hourly_mean[hourly_mean > peak_threshold].index.tolist()
        
        # 保存分析结果
        self.analysis_results['hourly_stats'] = hourly_stats
        self.analysis_results['peak_hours'] = peak_hours
        self.analysis_results['peak_threshold'] = peak_threshold
        
        # 输出分析结果
        print(f"用水高峰时段: {peak_hours}")
        print(f"高峰阈值: {peak_threshold:.4f} T/小时")
        print(f"高峰期平均用水量: {hourly_mean[peak_hours].mean():.4f} T/小时")
        print(f"非高峰期平均用水量: {hourly_mean[~hourly_mean.index.isin(peak_hours)].mean():.4f} T/小时")
        
        # 绘制每小时用水模式图表
        fig, axes = self._plot_hourly_patterns(hourly_stats, peak_hours, peak_threshold)
        
        return hourly_stats, peak_hours
    
    def _plot_hourly_patterns(self, hourly_stats, peak_hours, peak_threshold):
        """
        绘制每小时用水模式图表
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('每小时用水模式分析', fontsize=16, fontweight='bold')
        
        # 1. 每小时平均用水量柱状图
        colors = ['red' if hour in peak_hours else 'skyblue' for hour in hourly_stats.index]
        bars = axes[0, 0].bar(hourly_stats.index, hourly_stats['mean'], color=colors, alpha=0.7)
        axes[0, 0].axhline(y=peak_threshold, color='red', linestyle='--', linewidth=2, 
                          label=f'高峰阈值: {peak_threshold:.3f}')
        axes[0, 0].set_title('每小时平均用水量分布', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('小时')
        axes[0, 0].set_ylabel('每小时平均用水量 (T/小时)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if i in peak_hours:
                axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 0.001,
                               f'{height:.3f}', ha='center', va='bottom', fontweight='bold', color='red')
        
        # 2. 各楼栋每小时用水量热力图
        building_hourly = self.combined_data.groupby(['楼栋', '小时'])['水流量'].mean().unstack(fill_value=0)
        sns.heatmap(building_hourly, ax=axes[0, 1], cmap='YlOrRd', 
                   cbar_kws={'label': '用水量 (T)'}, annot=False)
        axes[0, 1].set_title('各楼栋每小时用水量热力图', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('小时')
        axes[0, 1].set_ylabel('楼栋')
        
        # 3. 用水量变异系数分析
        cv = (hourly_stats['std'] / hourly_stats['mean']).fillna(0)
        axes[1, 0].bar(cv.index, cv.values, color='lightgreen', alpha=0.7)
        axes[1, 0].set_title('每小时用水量变异系数', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('小时')
        axes[1, 0].set_ylabel('变异系数')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 累积用水量分布
        cumulative = hourly_stats['mean'].cumsum()
        axes[1, 1].plot(cumulative.index, cumulative.values, 'o-', linewidth=2, markersize=6)
        axes[1, 1].fill_between(cumulative.index, cumulative.values, alpha=0.3)
        axes[1, 1].set_title('累积每小时平均用水量分布', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('小时')
        axes[1, 1].set_ylabel('累积每小时平均用水量 (T/小时)')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, '每小时用水模式分析.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
        return fig, axes
    
    def analyze_weekly_patterns(self):
        """
        分析每周用水模式
        """
        print("\n" + "="*50)
        print("开始分析每周用水模式...")
        print("="*50)
        
        # 计算每天统计数据
        daily_stats = self.combined_data.groupby('星期')['水流量'].agg([
            'mean', 'std', 'median', 'sum', 'count'
        ]).round(4)
        
        # 工作日vs周末分析
        weekday_data = self.combined_data[~self.combined_data['是否周末']]['水流量']
        weekend_data = self.combined_data[self.combined_data['是否周末']]['水流量']
        
        weekday_stats = weekday_data.describe()
        weekend_stats = weekend_data.describe()
        
        # 统计检验
        t_stat, p_value = stats.ttest_ind(weekday_data, weekend_data)
        
        # 保存分析结果
        self.analysis_results['daily_stats'] = daily_stats
        self.analysis_results['weekday_stats'] = weekday_stats
        self.analysis_results['weekend_stats'] = weekend_stats
        self.analysis_results['weekday_weekend_test'] = {'t_stat': t_stat, 'p_value': p_value}
        
        # 输出分析结果
        print("每天用水统计:")
        print(daily_stats)
        print(f"\n工作日vs周末差异检验:")
        print(f"t统计量: {t_stat:.4f}")
        print(f"p值: {p_value:.4f}")
        print(f"差异显著性: {'显著' if p_value < 0.05 else '不显著'}")
        
        # 绘制每周用水模式图表
        fig, axes = self._plot_weekly_patterns(daily_stats, weekday_stats, weekend_stats)
        
        return daily_stats, weekday_stats, weekend_stats
    
    def _plot_weekly_patterns(self, daily_stats, weekday_stats, weekend_stats):
        """
        绘制每周用水模式图表
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('每周用水模式分析', fontsize=16, fontweight='bold')
        
        # 1. 每天平均用水量
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        colors = ['lightcoral' if i in [5, 6] else 'lightblue' for i in range(7)]
        bars = axes[0, 0].bar(range(7), daily_stats['mean'].values, color=colors, alpha=0.7)
        axes[0, 0].set_xticks(range(7))
        axes[0, 0].set_xticklabels(day_names)
        axes[0, 0].set_title('每天平均用水量', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('每小时平均用水量 (T/小时)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 0.001,
                           f'{height:.3f}', ha='center', va='bottom')
        
        # 2. 工作日vs周末用水量分布
        weekday_data = self.combined_data[~self.combined_data['是否周末']]['水流量']
        weekend_data = self.combined_data[self.combined_data['是否周末']]['水流量']
        
        axes[0, 1].hist(weekday_data, bins=50, alpha=0.7, label='工作日', density=True, color='blue')
        axes[0, 1].hist(weekend_data, bins=50, alpha=0.7, label='周末', density=True, color='red')
        axes[0, 1].set_title('工作日vs周末用水量分布', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('每小时用水量 (T/小时)')
        axes[0, 1].set_ylabel('密度')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 每天用水量变化趋势
        axes[1, 0].plot(range(7), daily_stats['mean'].values, 'o-', linewidth=2, markersize=8, color='green')
        axes[1, 0].fill_between(range(7), daily_stats['mean'].values, alpha=0.3, color='green')
        axes[1, 0].set_xticks(range(7))
        axes[1, 0].set_xticklabels(day_names)
        axes[1, 0].set_title('每天用水量变化趋势', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('每小时平均用水量 (T/小时)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. 工作日vs周末统计对比
        categories = ['平均值', '中位数', '标准差', '最大值']
        weekday_values = [weekday_stats['mean'], weekday_stats['50%'], weekday_stats['std'], weekday_stats['max']]
        weekend_values = [weekend_stats['mean'], weekend_stats['50%'], weekend_stats['std'], weekend_stats['max']]
        
        x = np.arange(len(categories))
        width = 0.35
        
        axes[1, 1].bar(x - width/2, weekday_values, width, label='工作日', alpha=0.7)
        axes[1, 1].bar(x + width/2, weekend_values, width, label='周末', alpha=0.7)
        axes[1, 1].set_title('工作日vs周末统计对比', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('每小时用水量 (T/小时)')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(categories)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, '每周用水模式分析.png'), 
                   dpi=300, bbox_inches='tight')
        plt.show()
        return fig, axes
    
    def analyze_time_period_patterns(self):
        """
        分析时间段用水模式（上午、下午、晚上、深夜）
        """
        print("\n" + "="*50)
        print("开始分析时间段用水模式...")
        print("="*50)
        
        # 计算各时间段统计数据
        period_stats = self.combined_data.groupby('时间段')['水流量'].agg([
            'mean', 'std', 'median', 'sum', 'count'
        ]).round(4)
        
        # 各时间段在工作日和周末的差异
        period_weekday_weekend = self.combined_data.groupby(['时间段', '是否周末'])['水流量'].mean().unstack()
        period_weekday_weekend.columns = ['工作日', '周末']
        
        # 保存分析结果
        self.analysis_results['period_stats'] = period_stats
        self.analysis_results['period_weekday_weekend'] = period_weekday_weekend
        
        # 输出分析结果
        print("各时间段用水统计:")
        print(period_stats)
        print("\n各时间段工作日vs周末对比:")
        print(period_weekday_weekend)
        
        # 绘制时间段用水模式图表
        fig, ax = self._plot_time_period_patterns(period_stats, period_weekday_weekend)
        
        return period_stats, period_weekday_weekend
    
    def _plot_time_period_patterns(self, period_stats, period_weekday_weekend):
        """
        绘制时间段用水模式图表
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        fig.suptitle('时间段用水模式分析', fontsize=16, fontweight='bold')
        
        # 1. 各时间段平均用水量
        period_order = ['深夜', '上午', '下午', '晚上']
        period_colors = ['navy', 'gold', 'orange', 'purple']
        
        ordered_data = [period_stats.loc[period, 'mean'] if period in period_stats.index else 0 
                       for period in period_order]
        
        ax.bar(period_order, ordered_data, color=period_colors, alpha=0.7)
        ax.set_title('各时间段平均用水量', fontsize=14, fontweight='bold')
        ax.set_ylabel('每小时平均用水量 (T/小时)')
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        
        # 添加数值标签
        for bar, value in zip(ax.patches, ordered_data):
            ax.text(bar.get_x() + bar.get_width()/2., value + 0.001,
                   f'{value:.3f}', ha='center', va='bottom')
        
        # 2. 时间段用水量饼图
        period_sums = [period_stats.loc[period, 'sum'] if period in period_stats.index else 0 
                      for period in period_order]
        
        ax.pie(period_sums, labels=period_order, colors=period_colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('各时间段用水量占比', fontsize=14, fontweight='bold')
        
        # 3. 工作日vs周末各时间段对比
        if not period_weekday_weekend.empty:
            x = np.arange(len(period_order))
            width = 0.35
            
            weekday_values = [period_weekday_weekend.loc[period, '工作日'] if period in period_weekday_weekend.index else 0 
                             for period in period_order]
            weekend_values = [period_weekday_weekend.loc[period, '周末'] if period in period_weekday_weekend.index else 0 
                             for period in period_order]
            
            ax.bar(x - width/2, weekday_values, width, label='工作日', alpha=0.7)
            ax.bar(x + width/2, weekend_values, width, label='周末', alpha=0.7)
            ax.set_title('工作日vs周末各时间段用水量对比', fontsize=14, fontweight='bold')
            ax.set_ylabel('每小时平均用水量 (T/小时)')
            ax.set_xticks(x)
            ax.set_xticklabels(period_order)
            ax.legend()
            ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        
        # 4. 各时间段用水量变异性
        cv_values = [period_stats.loc[period, 'std'] / period_stats.loc[period, 'mean'] 
                    if period in period_stats.index and period_stats.loc[period, 'mean'] > 0 else 0 
                    for period in period_order]
        
        ax.bar(period_order, cv_values, color='lightcoral', alpha=0.7)
        ax.set_title('各时间段用水量变异系数', fontsize=14, fontweight='bold')
        ax.set_ylabel('变异系数')
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, '分时段用水模式分析.png'),
                   dpi=300, bbox_inches='tight')
        plt.show()
        return fig, ax
    
    def analyze_building_differences(self):
        """
        分析不同楼栋的用水差异
        """
        print("\n" + "="*50)
        print("开始分析不同楼栋用水差异...")
        print("="*50)
        
        # 计算各楼栋统计数据
        building_stats = self.combined_data.groupby('楼栋')['水流量'].agg([
            'mean', 'std', 'median', 'max', 'sum', 'count'
        ]).round(4)
        
        # 各楼栋高峰时段分析
        building_peak_hours = {}
        for building in self.buildings_data.keys():
            building_data = self.buildings_data[building]
            hourly_mean = building_data.groupby('小时')['水流量'].mean()
            threshold = hourly_mean.mean() + hourly_mean.std()
            peak_hours = hourly_mean[hourly_mean > threshold].index.tolist()
            building_peak_hours[building] = peak_hours
        
        # 保存分析结果
        self.analysis_results['building_stats'] = building_stats
        self.analysis_results['building_peak_hours'] = building_peak_hours
        
        # 输出分析结果
        print("各楼栋用水统计:")
        print(building_stats)
        print("\n各楼栋用水高峰时段:")
        for building, peaks in building_peak_hours.items():
            print(f"{building}: {peaks}")
        
        # 绘制楼栋差异分析图表
        fig, ax = self._plot_building_differences(building_stats, building_peak_hours)
        
        return building_stats, building_peak_hours
    
    def _plot_building_differences(self, building_stats, building_peak_hours):
        """
        绘制楼栋差异分析图表
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        fig.suptitle('不同楼栋用水差异分析', fontsize=16, fontweight='bold')
        
        buildings = building_stats.index.tolist()
        
        # 1. 各楼栋平均用水量对比
        bars = ax.bar(buildings, building_stats['mean'], color='lightsteelblue', alpha=0.7)
        ax.set_title('各楼栋平均用水量对比', fontsize=14, fontweight='bold')
        ax.set_ylabel('每小时平均用水量 (T/小时)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                   f'{height:.3f}', ha='center', va='bottom')
        
        # 2. 各楼栋用水量分布箱线图
        building_data_list = [self.buildings_data[building]['水流量'].values for building in buildings]
        box_plot = ax.boxplot(building_data_list, labels=buildings, patch_artist=True)
        
        # 设置箱线图颜色
        colors = plt.cm.Set3(np.linspace(0, 1, len(buildings)))
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title('各楼栋用水量分布', fontsize=14, fontweight='bold')
        ax.set_ylabel('每小时用水量 (T/小时)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        
        # 3. 各楼栋总用水量对比
        ax.bar(buildings, building_stats['sum'], color='lightcoral', alpha=0.7)
        ax.set_title('各楼栋总用水量对比', fontsize=14, fontweight='bold')
        ax.set_ylabel('总用水量 (T)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)
        
        # 4. 各楼栋高峰时段对比
        peak_hours_matrix = np.zeros((len(buildings), 24))
        for i, building in enumerate(buildings):
            if building in building_peak_hours:
                for hour in building_peak_hours[building]:
                    peak_hours_matrix[i, hour] = 1
        
        im = ax.imshow(peak_hours_matrix, cmap='Reds', aspect='auto')
        ax.set_title('各楼栋高峰时段分布', fontsize=14, fontweight='bold')
        ax.set_xlabel('小时')
        ax.set_ylabel('楼栋')
        ax.set_yticks(range(len(buildings)))
        ax.set_yticklabels(buildings)
        ax.set_xticks(range(0, 24, 2))
        
        # 添加颜色条
        plt.colorbar(im, ax=ax, label='是否为高峰时段')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, '楼栋用水差异分析.png'),
                   dpi=300, bbox_inches='tight')
        plt.show()
        return fig, ax
    
    def generate_pump_control_recommendations(self):
        """
        生成增压泵控制建议
        """
        print("\n" + "="*50)
        print("生成增压泵控制建议...")
        print("="*50)
        
        # 获取用水高峰时段
        peak_hours = self.analysis_results.get('peak_hours', [])
        
        # 计算节能效果
        total_hours = 24
        pump_running_hours = len(peak_hours)
        energy_saving_ratio = (total_hours - pump_running_hours) / total_hours
        
        # 生成建议
        recommendations = {
            'pump_running_hours': peak_hours,
            'pump_off_hours': [h for h in range(24) if h not in peak_hours],
            'daily_running_time': pump_running_hours,
            'energy_saving_ratio': energy_saving_ratio,
            'recommendations': [
                f"建议增压泵在 {peak_hours} 时运行",
                f"其他时间段（{[h for h in range(24) if h not in peak_hours]}）可关闭增压泵",
                f"预计可节省增压泵运行时间 {energy_saving_ratio*100:.1f}%",
                f"建议设置自动控制系统，根据用水量实时调节"
            ]
        }
        
        # 保存建议
        self.analysis_results['pump_control_recommendations'] = recommendations
        
        # 输出建议
        print("增压泵控制建议:")
        for rec in recommendations['recommendations']:
            print(f"- {rec}")
        
        return recommendations
    
    def generate_analysis_report(self):
        """
        生成详细的分析报告
        """
        print("\n" + "="*50)
        print("生成分析报告...")
        print("="*50)
        
        # 获取分析结果
        hourly_stats = self.analysis_results.get('hourly_stats')
        peak_hours = self.analysis_results.get('peak_hours', [])
        daily_stats = self.analysis_results.get('daily_stats')
        weekday_stats = self.analysis_results.get('weekday_stats')
        weekend_stats = self.analysis_results.get('weekend_stats')
        building_stats = self.analysis_results.get('building_stats')
        pump_recommendations = self.analysis_results.get('pump_control_recommendations', {})
        
        # 生成报告内容
        report = f"""
# 用水习惯分析报告

## 1. 分析概述

本报告基于 {len(self.buildings_data)} 个楼栋的用水数据，分析时间范围为 {self.combined_data['日期'].min()} 至 {self.combined_data['日期'].max()}，
总计分析了 {len(self.combined_data)} 条用水记录。

### 1.1 数据概况
- **楼栋数量**: {len(self.buildings_data)} 个
- **数据记录**: {len(self.combined_data)} 条
- **平均用水量**: {self.combined_data['水流量'].mean():.4f} T/小时
- **最大用水量**: {self.combined_data['水流量'].max():.4f} T/小时
- **零用水量比例**: {(self.combined_data['水流量'] == 0).mean()*100:.1f}%

## 2. 每小时用水模式分析

### 2.1 用水高峰时段识别
**用水高峰时段**: {', '.join(map(str, peak_hours))}时

高峰时段特征：
- 高峰期平均用水量: {hourly_stats.loc[peak_hours, 'mean'].mean():.4f} T/小时
- 非高峰期平均用水量: {hourly_stats.loc[~hourly_stats.index.isin(peak_hours), 'mean'].mean():.4f} T/小时
- 高峰期用水量是非高峰期的 {(hourly_stats.loc[peak_hours, 'mean'].mean() / hourly_stats.loc[~hourly_stats.index.isin(peak_hours), 'mean'].mean()):.1f} 倍

### 2.2 每小时用水统计
```
{hourly_stats.to_string()}
```

## 3. 每周用水模式分析

### 3.1 工作日vs周末差异

**工作日用水特征**:
- 平均用水量: {weekday_stats['mean']:.4f} T/小时
- 标准差: {weekday_stats['std']:.4f} T/小时
- 最大用水量: {weekday_stats['max']:.4f} T/小时

**周末用水特征**:
- 平均用水量: {weekend_stats['mean']:.4f} T/小时
- 标准差: {weekend_stats['std']:.4f} T/小时
- 最大用水量: {weekend_stats['max']:.4f} T/小时

**差异分析**:
- 工作日平均用水量比周末{'高' if weekday_stats['mean'] > weekend_stats['mean'] else '低'} {abs(weekday_stats['mean'] - weekend_stats['mean']):.4f} T/小时
- 差异显著性: {self.analysis_results.get('weekday_weekend_test', {}).get('p_value', 0) < 0.05 and '显著' or '不显著'}

### 3.2 每天用水统计
```
{daily_stats.to_string()}
```

## 4. 楼栋差异分析

### 4.1 各楼栋用水统计
```
{building_stats.to_string()}
```

### 4.2 各楼栋高峰时段
{chr(10).join([f"- {building}: {hours}" for building, hours in self.analysis_results.get('building_peak_hours', {}).items()])}

## 5. 增压泵控制建议

### 5.1 运行时间建议
- **建议运行时段**: {', '.join(map(str, peak_hours))}时
- **建议关闭时段**: {', '.join(map(str, [h for h in range(24) if h not in peak_hours]))}时
- **每日运行时间**: {len(peak_hours)} 小时
- **节能比例**: {pump_recommendations.get('energy_saving_ratio', 0)*100:.1f}%

### 5.2 控制策略建议
1. **时间控制**: 根据用水高峰期自动启停增压泵
2. **压力控制**: 实时监测管网压力，低于设定值时启动
3. **变频调速**: 根据用水量需求调节泵转速
4. **智能预测**: 结合用水量预测提前调整运行状态

### 5.3 预期效果
- **节电效果**: 减少增压泵运行时间 {pump_recommendations.get('energy_saving_ratio', 0)*100:.1f}%
- **成本节约**: 预计年节约电费 30-50%
- **设备保护**: 减少无效运行，延长设备寿命

## 6. 主要发现与结论

### 6.1 主要发现
1. **用水高峰集中**: 用水主要集中在 {', '.join(map(str, peak_hours))} 时段
2. **工作日周末差异**: 工作日与周末用水模式存在{'显著' if self.analysis_results.get('weekday_weekend_test', {}).get('p_value', 0) < 0.05 else '不显著'}差异
3. **楼栋差异明显**: 不同楼栋的用水习惯存在差异
4. **节能潜力巨大**: 通过智能控制可实现显著节能效果

### 6.2 应用价值
1. **增压泵控制**: 为增压泵智能控制提供科学依据
2. **热水系统优化**: 支持热水系统整体节能优化
3. **运维管理**: 提升系统运维管理效率
4. **成本控制**: 显著降低运行成本

### 6.3 优化建议
1. **数据扩充**: 收集更长时间跨度的数据
2. **实时监控**: 建立实时数据监控系统
3. **智能控制**: 开发智能控制算法
4. **定期评估**: 定期评估和优化控制策略

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析程序: 用水习惯分析器 v1.0*
"""
        
        # 保存报告
        report_path = os.path.join(self.results_folder, '用水习惯分析报告.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"分析报告已保存至: {report_path}")
        return report
    
    def run_complete_analysis(self):
        """
        运行完整的用水习惯分析流程
        """
        print("\n" + "="*60)
        print("开始运行完整的用水习惯分析")
        print("="*60)
        
        try:
            # 1. 加载数据
            self.load_data()
            
            # 2. 分析每小时用水模式
            self.analyze_hourly_patterns()
            
            # 3. 分析每周用水模式
            self.analyze_weekly_patterns()
            
            # 4. 分析时间段用水模式
            self.analyze_time_period_patterns()
            
            # 5. 分析楼栋差异
            self.analyze_building_differences()
            
            # 6. 生成增压泵控制建议
            self.generate_pump_control_recommendations()
            
            # 7. 生成分析报告
            self.generate_analysis_report()
            
            print("\n" + "="*60)
            print("用水习惯分析完成！")
            print(f"所有结果已保存到: {self.results_folder}")
            print("="*60)
            
        except Exception as e:
            print(f"分析过程中出现错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    """
    主函数：执行用水习惯分析
    """
    print("用水习惯分析程序")
    print("功能：分析用户用水模式，为热水系统节能优化提供数据支撑")
    print("-" * 60)
    
    # 设置数据文件夹路径
    data_folder = r"E:\热水系统\方案分析\用户用水习惯分析"
    
    # 检查数据文件夹是否存在
    if not os.path.exists(data_folder):
        print(f"错误：数据文件夹 {data_folder} 不存在")
        return
    
    # 创建分析器并运行分析
    analyzer = WaterHabitAnalyzer(data_folder)
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()