#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用水习惯分析程序 - Web服务适配版
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
import io
import base64
from scipy import stats
from sklearn.cluster import KMeans
from collections import Counter
from flask import current_app
import matplotlib.font_manager as fm

class WaterHabitAnalyzer:
    """
    用水习惯分析器 - Web服务版
    """
    
    def __init__(self, data_folder, filenames):
        self.data_folder = data_folder
        self.filenames = filenames
        self.buildings_data = {}
        self.combined_data = None
        self.analysis_results = {}
        self._configure_matplotlib()
        
    def _configure_matplotlib(self):
        """
        设置matplotlib绘图参数，强制使用项目自带的中文字体，并确保缓存更新。
        """
        plt.switch_backend('Agg')
        try:
            # 构建字体文件的绝对路径
            font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts')
            font_path = os.path.join(font_dir, 'SourceHanSansCN-Regular.ttf')

            if os.path.exists(font_path):
                # 清理并重建字体缓存，以确保新字体能被识别
                try:
                    # The '()' is important as of matplotlib 3.8+
                    fm.fontManager = fm.FontManager()
                    print("Matplotlib font manager cache forcefully rebuilt.")
                except Exception as e:
                    print(f"Could not rebuild font cache: {e}. This might be fine.")

                # 设置matplotlib字体
                prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()
                # Also set sans-serif as a fallback
                plt.rcParams['font.sans-serif'] = [prop.get_name()]
                print(f"成功加载并设置字体: {prop.get_name()}")
            else:
                print(f"警告: 在路径 {font_path} 未找到指定的字体文件。将回退到默认字体，中文可能无法显示。")
                plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']

            plt.rcParams['axes.unicode_minus'] = False
        except Exception as e:
            print(f"设置matplotlib字体时发生错误: {e}")

        plt.rcParams['font.size'] = 12
        sns.set_style("whitegrid")
        warnings.filterwarnings('ignore')

    def _get_font_prop(self):
        """Helper to get font properties consistently."""
        try:
            font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts')
            font_path = os.path.join(font_dir, 'SourceHanSansCN-Regular.ttf')
            if os.path.exists(font_path):
                return fm.FontProperties(fname=font_path)
        except Exception:
            return None

    def load_data(self):
        all_dfs = []
        csv_files = [os.path.join(self.data_folder, f) for f in self.filenames]
        if not csv_files:
            raise FileNotFoundError("没有提供任何数据文件。")

        for file_path in csv_files:
            building_name = os.path.basename(file_path).replace('.csv', '').replace('_水流量数据', '')
            df = pd.read_csv(file_path, encoding='utf-8')
            df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
            df['datetime'] = df['日期'] + pd.to_timedelta(df['小时'], unit='h')
            df['月份'] = df['日期'].dt.month
            df['日'] = df['日期'].dt.day
            df['是否周末'] = df['星期'].isin([6, 7])
            if '水流量' in df.columns and '用水量' not in df.columns:
                 df.rename(columns={'水流量': '用水量'}, inplace=True)
            df['时间段'] = df['小时'].apply(self._get_time_period)
            df['楼栋'] = building_name
            all_dfs.append(df)
            self.buildings_data[building_name] = df
        
        if all_dfs:
            self.combined_data = pd.concat(all_dfs, ignore_index=True)

    def _get_time_period(self, hour):
        if 6 <= hour < 12: return '上午'
        elif 12 <= hour < 18: return '下午'
        elif 18 <= hour < 24: return '晚上'
        else: return '深夜'

    def _save_plot_to_base64(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=200, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        return img_str

    def analyze_hourly_patterns(self):
        hourly_stats = self.combined_data.groupby('小时')['用水量'].agg(['mean', 'std', 'median', 'max', 'count']).round(4)
        hourly_mean = hourly_stats['mean']
        peak_threshold = hourly_mean.mean() + hourly_mean.std()
        peak_hours = hourly_mean[hourly_mean > peak_threshold].index.tolist()
        self.analysis_results['hourly_stats'] = hourly_stats
        self.analysis_results['peak_hours'] = peak_hours
        self.analysis_results['peak_threshold'] = peak_threshold
        return hourly_stats, peak_hours, peak_threshold

    def _plot_hourly_patterns(self, hourly_stats, peak_hours, peak_threshold):
        font_prop = self._get_font_prop()
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('每小时用水模式分析', fontsize=16, fontweight='bold', fontproperties=font_prop)
        colors = ['red' if hour in peak_hours else 'skyblue' for hour in hourly_stats.index]
        bars = axes[0, 0].bar(hourly_stats.index, hourly_stats['mean'], color=colors, alpha=0.7)
        axes[0, 0].axhline(y=peak_threshold, color='red', linestyle='--', linewidth=2, label=f'高峰阈值: {peak_threshold:.3f}')
        axes[0, 0].set_title('每小时平均用水量分布', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('小时')
        axes[0, 0].set_ylabel('每小时平均用水量 (T/小时)')
        axes[0, 0].legend()
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if hourly_stats.index[i] in peak_hours:
                axes[0, 0].text(bar.get_x() + bar.get_width()/2., height, f'{height:.3f}', ha='center', va='bottom', fontweight='bold', color='red')
        building_hourly = self.combined_data.groupby(['楼栋', '小时'])['用水量'].mean().unstack(fill_value=0)
        sns.heatmap(building_hourly, ax=axes[0, 1], cmap='YlOrRd', cbar_kws={'label': '用水量 (T)'}, annot=False)
        axes[0, 1].set_title('各楼栋每小时用水量热力图', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('小时')
        axes[0, 1].set_ylabel('楼栋')
        cv = (hourly_stats['std'] / hourly_stats['mean']).fillna(0)
        axes[1, 0].bar(cv.index, cv.values, color='lightgreen', alpha=0.7)
        axes[1, 0].set_title('每小时用水量变异系数', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('小时')
        axes[1, 0].set_ylabel('变异系数')
        cumulative = hourly_stats['mean'].cumsum()
        axes[1, 1].plot(cumulative.index, cumulative.values, 'o-', linewidth=2, markersize=6)
        axes[1, 1].fill_between(cumulative.index, cumulative.values, alpha=0.3)
        axes[1, 1].set_title('累积每小时平均用水量分布', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('小时')
        axes[1, 1].set_ylabel('累积每小时平均用水量 (T/小时)')
        # Apply font properties to all text elements
        for ax_row in axes:
            for ax in ax_row:
                for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels() + ax.get_legend_handles_labels()[1]):
                    if hasattr(item, 'set_fontproperties'):
                        item.set_fontproperties(font_prop)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        return self._save_plot_to_base64(fig)
    
    def analyze_weekly_patterns(self):
        daily_stats = self.combined_data.groupby('星期')['用水量'].agg(['mean', 'std', 'median', 'sum', 'count']).round(4)
        weekday_data = self.combined_data[~self.combined_data['是否周末']]['用水量']
        weekend_data = self.combined_data[self.combined_data['是否周末']]['用水量']
        weekday_stats = weekday_data.describe()
        weekend_stats = weekend_data.describe()
        t_stat, p_value = stats.ttest_ind(weekday_data, weekend_data, equal_var=False)
        self.analysis_results['daily_stats'] = daily_stats
        self.analysis_results['weekday_stats'] = weekday_stats
        self.analysis_results['weekend_stats'] = weekend_stats
        self.analysis_results['weekday_weekend_test'] = {'t_stat': t_stat, 'p_value': p_value}
        return daily_stats, weekday_stats, weekend_stats

    def _plot_weekly_patterns(self, daily_stats, weekday_stats, weekend_stats):
        font_prop = self._get_font_prop()
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('每周用水模式分析', fontsize=16, fontweight='bold', fontproperties=font_prop)
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        colors = ['lightcoral' if i >= 5 else 'lightblue' for i in range(7)]
        bars = axes[0, 0].bar(range(7), daily_stats['mean'].reindex(range(1,8)).fillna(0).values, color=colors, alpha=0.7)
        axes[0, 0].set_xticks(range(7))
        axes[0, 0].set_xticklabels(day_names)
        axes[0, 0].set_title('每天平均用水量', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('每小时平均用水量 (T/小时)')
        for bar in bars:
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height, f'{height:.3f}', ha='center', va='bottom')
        weekday_data = self.combined_data[~self.combined_data['是否周末']]['用水量']
        weekend_data = self.combined_data[self.combined_data['是否周末']]['用水量']
        sns.histplot(weekday_data, bins=50, alpha=0.7, label='工作日', ax=axes[0, 1], kde=True)
        sns.histplot(weekend_data, bins=50, alpha=0.7, label='周末', ax=axes[0, 1], kde=True)
        axes[0, 1].set_title('工作日vs周末用水量分布', fontsize=14, fontweight='bold')
        axes[0, 1].legend()
        axes[1, 0].plot(range(7), daily_stats['mean'].reindex(range(1,8)).fillna(0).values, 'o-', linewidth=2, markersize=8, color='green')
        axes[1, 0].fill_between(range(7), daily_stats['mean'].reindex(range(1,8)).fillna(0).values, alpha=0.3, color='green')
        axes[1, 0].set_xticks(range(7))
        axes[1, 0].set_xticklabels(day_names)
        axes[1, 0].set_title('每天用水量变化趋势', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('每小时平均用水量 (T/小时)')
        categories = ['mean', '50%', 'std', 'max']
        labels = {'mean': '平均值', '50%': '中位数', 'std': '标准差', 'max': '最大值'}
        weekday_values = [weekday_stats[cat] for cat in categories]
        weekend_values = [weekend_stats[cat] for cat in categories]
        x = np.arange(len(categories))
        width = 0.35
        axes[1, 1].bar(x - width/2, weekday_values, width, label='工作日', alpha=0.7)
        axes[1, 1].bar(x + width/2, weekend_values, width, label='周末', alpha=0.7)
        axes[1, 1].set_title('工作日vs周末统计对比', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('每小时用水量 (T/小时)')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels([labels[cat] for cat in categories])
        axes[1, 1].legend()
        # Apply font properties to all text elements
        for ax_row in axes:
            for ax in ax_row:
                for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels() + ax.get_legend_handles_labels()[1]):
                    if hasattr(item, 'set_fontproperties'):
                        item.set_fontproperties(font_prop)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        return self._save_plot_to_base64(fig)
    
    def analyze_time_period_patterns(self):
        period_stats = self.combined_data.groupby('时间段')['用水量'].agg(['mean', 'std', 'median', 'sum', 'count']).round(4)
        period_weekday_weekend = self.combined_data.groupby(['时间段', '是否周末'])['用水量'].mean().unstack()
        if not period_weekday_weekend.empty:
            period_weekday_weekend.columns = ['工作日', '周末']
        self.analysis_results['period_stats'] = period_stats
        self.analysis_results['period_weekday_weekend'] = period_weekday_weekend
        return period_stats, period_weekday_weekend

    def _plot_time_period_patterns(self, period_stats, period_weekday_weekend):
        font_prop = self._get_font_prop()
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('分时段用水模式分析', fontsize=16, fontweight='bold', fontproperties=font_prop)
        period_order = ['上午', '下午', '晚上', '深夜']
        period_colors = ['gold', 'orange', 'purple', 'navy']
        ordered_data = period_stats['mean'].reindex(period_order).fillna(0)
        axes[0, 0].bar(ordered_data.index, ordered_data.values, color=period_colors, alpha=0.7)
        axes[0, 0].set_title('各时间段平均用水量', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('每小时平均用水量 (T/小时)')
        period_sums = period_stats['sum'].reindex(period_order).fillna(0)
        
        # Explicitly set font properties for pie chart text elements
        wedges, texts, autotexts = axes[0, 1].pie(period_sums, labels=period_sums.index, colors=period_colors, autopct='%1.1f%%', startangle=90)
        for text in texts:
            text.set_fontproperties(font_prop)
        for autotext in autotexts:
            autotext.set_fontproperties(font_prop)

        axes[0, 1].set_title('各时间段用水量占比', fontsize=14, fontweight='bold')

        if not period_weekday_weekend.empty:
            x = np.arange(len(period_order))
            width = 0.35
            weekday_values = period_weekday_weekend['工作日'].reindex(period_order).fillna(0)
            weekend_values = period_weekday_weekend['周末'].reindex(period_order).fillna(0)
            axes[1, 0].bar(x - width/2, weekday_values, width, label='工作日', alpha=0.7)
            axes[1, 0].bar(x + width/2, weekend_values, width, label='周末', alpha=0.7)
            axes[1, 0].set_title('工作日vs周末各时间段用水量对比', fontsize=14, fontweight='bold')
            axes[1, 0].set_ylabel('每小时平均用水量 (T/小时)')
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels(period_order)
            axes[1, 0].legend()
        cv_values = (period_stats['std'] / period_stats['mean']).reindex(period_order).fillna(0)
        axes[1, 1].bar(cv_values.index, cv_values.values, color='lightcoral', alpha=0.7)
        axes[1, 1].set_title('各时间段用水量变异系数', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('变异系数')
        # Apply font properties to all text elements
        for ax_row in axes:
            for ax in ax_row:
                for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels() + ax.get_legend_handles_labels()[1]):
                    if hasattr(item, 'set_fontproperties'):
                        item.set_fontproperties(font_prop)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        return self._save_plot_to_base64(fig)

    def analyze_building_differences(self):
        building_stats = self.combined_data.groupby('楼栋')['用水量'].agg(['mean', 'std', 'median', 'max', 'sum', 'count']).round(4)
        building_peak_hours = {}
        for building, df in self.combined_data.groupby('楼栋'):
            hourly_mean = df.groupby('小时')['用水量'].mean()
            threshold = hourly_mean.mean() + hourly_mean.std()
            peak_hours = hourly_mean[hourly_mean > threshold].index.tolist()
            building_peak_hours[building] = peak_hours
        self.analysis_results['building_stats'] = building_stats
        self.analysis_results['building_peak_hours'] = building_peak_hours
        return building_stats, building_peak_hours

    def _plot_building_differences(self, building_stats, building_peak_hours):
        font_prop = self._get_font_prop()
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('不同楼栋用水差异分析', fontsize=16, fontweight='bold', fontproperties=font_prop)
        buildings = building_stats.index.tolist()

        # 子图 1: 各楼栋平均用水量对比 (柱状图)
        axes[0, 0].bar(buildings, building_stats['mean'], color='lightsteelblue', alpha=0.7)
        axes[0, 0].set_title('各楼栋平均用水量对比', fontsize=14, fontweight='bold')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # 子图 2: 各楼栋用水量分布 (箱线图) - 增加更严格的数据验证
        building_data_list = []
        valid_building_labels = []
        for b in buildings:
            # 确保楼栋数据存在，且 '用水量' 列存在且不为空
            if b in self.buildings_data and '用水量' in self.buildings_data[b].columns:
                # 移除NaN值并转换为numpy数组
                data_series = self.buildings_data[b]['用水量'].dropna()
                if not data_series.empty:
                    building_data_list.append(data_series.values)
                    valid_building_labels.append(b)
                else:
                    current_app.logger.warning(f"楼栋 '{b}' 的用水量数据为空或全是NaN，已在箱线图中跳过。")
            else:
                current_app.logger.warning(f"楼栋 '{b}' 的数据不存在或缺少'用水量'列，已在箱线图中跳过。")

        if building_data_list:
            axes[0, 1].boxplot(building_data_list, labels=valid_building_labels, patch_artist=True)
        else:
            axes[0, 1].text(0.5, 0.5, '无有效数据用于绘制箱线图', ha='center', va='center', fontproperties=font_prop)
        
        axes[0, 1].set_title('各楼栋用水量分布', fontsize=14, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 子图 3: 各楼栋总用水量对比 (柱状图)
        axes[1, 0].bar(buildings, building_stats['sum'], color='lightcoral', alpha=0.7)
        axes[1, 0].set_title('各楼栋总用水量对比', fontsize=14, fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # 子图 4: 各楼栋高峰时段分布 (热力图)
        peak_hours_matrix = np.zeros((len(buildings), 24))
        for i, building in enumerate(buildings):
            if building in building_peak_hours:
                for hour in building_peak_hours.get(building, []):
                    peak_hours_matrix[i, hour] = 1
        im = axes[1, 1].imshow(peak_hours_matrix, cmap='Reds', aspect='auto')
        axes[1, 1].set_title('各楼栋高峰时段分布', fontsize=14, fontweight='bold')
        axes[1, 1].set_yticks(range(len(buildings)))
        axes[1, 1].set_yticklabels(buildings)
        plt.colorbar(im, ax=axes[1, 1], label='高峰时段出现')
        
        # Apply font properties to all text elements
        for ax_row in axes:
            for ax in ax_row:
                for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels() + ax.get_legend_handles_labels()[1]):
                    if hasattr(item, 'set_fontproperties'):
                        item.set_fontproperties(font_prop)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        return self._save_plot_to_base64(fig)
    
    def analyze_pump_control(self):
        """
        Generates pump control recommendations based on peak hours.
        """
        if 'peak_hours' not in self.analysis_results:
            return {}
            
        peak_hours = self.analysis_results['peak_hours']
        total_hours = 24
        running_hours = len(peak_hours)
        
        energy_saving_ratio = (total_hours - running_hours) / total_hours if total_hours > 0 else 0
        
        recommendations = {
            'running_hours': running_hours,
            'peak_hours': peak_hours,
            'off_hours': [h for h in range(total_hours) if h not in peak_hours],
            'energy_saving_ratio': energy_saving_ratio,
        }
        self.analysis_results['pump_control_recommendations'] = recommendations
        return recommendations

    def perform_clustering(self):
        daily_profiles = self.combined_data.pivot_table(index='日期', columns='小时', values='用水量', fill_value=0)
        sse = {}
        optimal_k = 3
        if daily_profiles.shape[0] > 1:
            for k in range(2, min(8, daily_profiles.shape[0])):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto').fit(daily_profiles)
                sse[k] = kmeans.inertia_
            if sse:
                optimal_k = min(sse, key=sse.get)
        
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init='auto').fit(daily_profiles)
        daily_profiles['cluster'] = kmeans.labels_
        self.analysis_results['clustering_results'] = daily_profiles
        self.analysis_results['optimal_k'] = optimal_k
        return daily_profiles, optimal_k

    def _plot_clustering_patterns(self, daily_profiles, optimal_k):
        font_prop = self._get_font_prop()
        fig, axes = plt.subplots(optimal_k, 1, figsize=(14, 4 * optimal_k), sharex=True, sharey=True)
        if optimal_k == 1:
            axes = [axes] # Ensure axes is always a list
        fig.suptitle(f'{optimal_k}种典型日用水模式 (聚类分析)', fontsize=18, fontweight='bold', fontproperties=font_prop)
        
        for i, ax in enumerate(axes):
            cluster_data = daily_profiles[daily_profiles['cluster'] == i].drop('cluster', axis=1)

            if cluster_data.empty:
                ax.text(0.5, 0.5, '无数据', horizontalalignment='center', verticalalignment='center', fontproperties=font_prop)
                ax.set_title(f'模式 {i+1} (0 天)', fontsize=14, fontproperties=font_prop)
                continue

            x_values = pd.to_numeric(cluster_data.columns)
            mean_values = cluster_data.mean(axis=0)
            min_values = cluster_data.min(axis=0)
            max_values = cluster_data.max(axis=0)

            ax.plot(x_values, mean_values, label=f'模式 {i+1} (共 {len(cluster_data)} 天)', marker='o')
            ax.fill_between(x_values, min_values, max_values, alpha=0.2)
            ax.set_title(f'模式 {i+1} - 均值曲线与范围', fontsize=12, fontproperties=font_prop)
            ax.set_ylabel('平均用水量 (T/小时)', fontproperties=font_prop)
            ax.legend(prop=font_prop)
            ax.grid(True, linestyle='--', alpha=0.6)

        axes[-1].set_xlabel('小时', fontproperties=font_prop)
        
        # This loop is redundant now because we handle the single-axis case above
        # Apply font properties to all text elements
        for ax in axes:
            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
                if hasattr(item, 'set_fontproperties'):
                    item.set_fontproperties(font_prop)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        return self._save_plot_to_base64(fig)

    def generate_analysis_report(self):
        """
        生成基于用户提供的模板的详细Markdown分析报告。
        """
        # 从 self.analysis_results 安全地获取所有需要的数据
        hourly_stats = self.analysis_results.get('hourly_stats')
        peak_hours = self.analysis_results.get('peak_hours', [])
        daily_stats = self.analysis_results.get('daily_stats')
        weekday_stats = self.analysis_results.get('weekday_stats')
        weekend_stats = self.analysis_results.get('weekend_stats')
        building_stats = self.analysis_results.get('building_stats')
        building_peak_hours = self.analysis_results.get('building_peak_hours', {})
        pump_recommendations = self.analysis_results.get('pump_control_recommendations', {})
        p_value = self.analysis_results.get('weekday_weekend_test', {}).get('p_value', 1.0)

        # 准备报告中可能用到的变量，并设置默认值以防数据缺失
        building_count = len(self.buildings_data)
        start_date = self.combined_data['日期'].min().strftime('%Y-%m-%d') if not self.combined_data.empty else 'N/A'
        end_date = self.combined_data['日期'].max().strftime('%Y-%m-%d') if not self.combined_data.empty else 'N/A'
        record_count = len(self.combined_data)
        mean_usage = self.combined_data['用水量'].mean() if not self.combined_data.empty else 0
        max_usage = self.combined_data['用水量'].max() if not self.combined_data.empty else 0
        zero_usage_ratio = (self.combined_data['用水量'] == 0).mean() * 100 if not self.combined_data.empty else 0
        
        peak_mean = hourly_stats.loc[peak_hours, 'mean'].mean() if hourly_stats is not None and peak_hours else 0
        non_peak_mean = hourly_stats.loc[~hourly_stats.index.isin(peak_hours), 'mean'].mean() if hourly_stats is not None else 0
        peak_ratio = (peak_mean / non_peak_mean) if non_peak_mean > 0 else 0

        weekday_mean = weekday_stats['mean'] if weekday_stats is not None else 0
        weekday_std = weekday_stats['std'] if weekday_stats is not None else 0
        weekday_max = weekday_stats['max'] if weekday_stats is not None else 0
        
        weekend_mean = weekend_stats['mean'] if weekend_stats is not None else 0
        weekend_std = weekend_stats['std'] if weekend_stats is not None else 0
        weekend_max = weekend_stats['max'] if weekend_stats is not None else 0

        weekday_weekend_comp = '高' if weekday_mean > weekend_mean else '低'
        weekday_weekend_diff = abs(weekday_mean - weekend_mean)
        p_test_result = '显著' if p_value < 0.05 else '不显著'

        building_peak_hours_str = "\n".join([f"- {building}: {', '.join(map(str, hours))}" for building, hours in building_peak_hours.items()])

        # 使用 f-string 和模板生成报告
        report = f"""
# 用水习惯分析报告

## 1. 分析概述

本报告基于 {building_count} 个楼栋的用水数据，分析时间范围为 {start_date} 至 {end_date}，
总计分析了 {record_count} 条用水记录。

### 1.1 数据概况
- **楼栋数量**: {building_count} 个
- **数据记录**: {record_count} 条
- **平均用水量**: {mean_usage:.4f} T/小时
- **最大用水量**: {max_usage:.4f} T/小时
- **零用水量比例**: {zero_usage_ratio:.1f}%

## 2. 每小时用水模式分析

### 2.1 用水高峰时段识别
**用水高峰时段**: {', '.join(map(str, peak_hours))}时

高峰时段特征：
- 高峰期平均用水量: {peak_mean:.4f} T/小时
- 非高峰期平均用水量: {non_peak_mean:.4f} T/小时
- 高峰期用水量是非高峰期的 {peak_ratio:.1f} 倍

### 2.2 每小时用水统计
```
{hourly_stats.to_string() if hourly_stats is not None else "N/A"}
```

## 3. 每周用水模式分析

### 3.1 工作日vs周末差异

**工作日用水特征**:
- 平均用水量: {weekday_mean:.4f} T/小时
- 标准差: {weekday_std:.4f} T/小时
- 最大用水量: {weekday_max:.4f} T/小时

**周末用水特征**:
- 平均用水量: {weekend_mean:.4f} T/小时
- 标准差: {weekend_std:.4f} T/小时
- 最大用水量: {weekend_max:.4f} T/小时

**差异分析**:
- 工作日平均用水量比周末{weekday_weekend_comp} {weekday_weekend_diff:.4f} T/小时
- 差异显著性: {p_test_result}

### 3.2 每天用水统计
```
{daily_stats.to_string() if daily_stats is not None else "N/A"}
```

## 4. 楼栋差异分析

### 4.1 各楼栋用水统计
```
{building_stats.to_string() if building_stats is not None else "N/A"}
```

### 4.2 各楼栋高峰时段
{building_peak_hours_str}

## 5. 增压泵控制建议

### 5.1 运行时间建议
- **建议运行时段**: {', '.join(map(str, pump_recommendations.get('peak_hours', [])))}时
- **建议关闭时段**: {', '.join(map(str, pump_recommendations.get('off_hours', [])))}时
- **每日运行时间**: {pump_recommendations.get('running_hours', 0)} 小时
- **节能比例**: {pump_recommendations.get('energy_saving_ratio', 0) * 100:.1f}%

### 5.2 控制策略建议
1. **时间控制**: 根据用水高峰期自动启停增压泵
2. **压力控制**: 实时监测管网压力，低于设定值时启动
3. **变频调速**: 根据用水量需求调节泵转速
4. **智能预测**: 结合用水量预测提前调整运行状态

### 5.3 预期效果
- **节电效果**: 减少增压泵运行时间 {pump_recommendations.get('energy_saving_ratio', 0) * 100:.1f}%
- **成本节约**: 预计年节约电费 30-50%
- **设备保护**: 减少无效运行，延长设备寿命

## 6. 主要发现与结论

### 6.1 主要发现
1. **用水高峰集中**: 用水主要集中在 {', '.join(map(str, peak_hours))} 时段
2. **工作日周末差异**: 工作日与周末用水模式存在{p_test_result}差异
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
        self.analysis_results['full_report'] = report
        return report

    def run_complete_analysis(self):
        self.load_data()
        
        if self.combined_data is None or self.combined_data.empty:
            report_text = "错误: 未加载任何有效数据，无法进行分析。"
            return {"report": report_text, "charts": []}

        charts = []
        
        hourly_stats, peak_hours, peak_threshold = self.analyze_hourly_patterns()
        charts.append({'title': '每小时用水模式分析', 'image_base64': self._plot_hourly_patterns(hourly_stats, peak_hours, peak_threshold)})
        
        daily_stats, weekday_stats, weekend_stats = self.analyze_weekly_patterns()
        charts.append({'title': '每周用水模式分析', 'image_base64': self._plot_weekly_patterns(daily_stats, weekday_stats, weekend_stats)})

        period_stats, period_weekday_weekend = self.analyze_time_period_patterns()
        charts.append({'title': '分时段用水模式分析', 'image_base64': self._plot_time_period_patterns(period_stats, period_weekday_weekend)})
        
        building_stats, building_peak_hours = self.analyze_building_differences()
        charts.append({'title': '楼栋用水差异分析', 'image_base64': self._plot_building_differences(building_stats, building_peak_hours)})

        # NEW: Run pump control analysis
        self.analyze_pump_control()

        daily_profiles, optimal_k = self.perform_clustering()
        charts.append({'title': '典型日用水模式聚类', 'image_base64': self._plot_clustering_patterns(daily_profiles, optimal_k)})

        report = self.generate_analysis_report()
        
        return {"report": report, "charts": charts}