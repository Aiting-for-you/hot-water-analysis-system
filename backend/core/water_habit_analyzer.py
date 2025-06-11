import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
import glob
from sklearn.cluster import KMeans
import zipfile

# --- Matplotlib and Seaborn Configuration ---
def configure_matplotlib(font_path=None):
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12
    plt.rcParams['figure.figsize'] = (12, 8)
    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.2)
    warnings.filterwarnings('ignore')
    if font_path and os.path.exists(font_path):
        plt.rcParams['font.sans-serif'] = [plt.matplotlib.font_manager.FontProperties(fname=font_path).get_name()]
        print(f"Using font: {font_path}")
    else:
        # Fallback fonts
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        print("Warning: Custom font not found. Using default fonts. Chinese characters may not display correctly.")

class WaterHabitAnalyzer:
    def __init__(self, input_file_path, results_folder, font_path=None):
        self.input_file_path = input_file_path
        self.results_folder = results_folder
        self.building_name = os.path.basename(input_file_path).replace('.csv', '')
        self.data = None
        self.analysis_results = {}
        
        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)
        
        configure_matplotlib(font_path)
        print(f"WaterHabitAnalyzer initialized for {self.building_name}")
        print(f"Results will be saved to: {self.results_folder}")

    def load_and_preprocess_data(self):
        print("\n" + "="*50)
        print(f"Loading and preprocessing data for {self.building_name}...")
        print("="*50)
        
        try:
            df = pd.read_csv(self.input_file_path, encoding='utf-8')
            
            # --- Data Preprocessing ---
            df['日期'] = pd.to_datetime(df['日期'], format='%Y%m%d')
            df['datetime'] = df['日期'] + pd.to_timedelta(df['小时'], unit='h')
            df['月份'] = df['日期'].dt.month
            df['日'] = df['日期'].dt.day
            df['是否周末'] = df['星期'].isin([6, 7])
            df['时间段'] = df['小时'].apply(self._get_time_period)
            
            self.data = df
            print(f"✓ Data loaded successfully for {self.building_name} with {len(df)} records.")
            return True
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False

    def _get_time_period(self, hour):
        if 6 <= hour < 12: return '上午'
        elif 12 <= hour < 18: return '下午'
        elif 18 <= hour < 24: return '晚上'
        else: return '深夜'

    def analyze_hourly_patterns(self):
        print("\nAnalyzing hourly patterns...")
        hourly_stats = self.data.groupby('小时')['水流量'].agg(['mean', 'std', 'median', 'max']).round(4)
        peak_threshold = hourly_stats['mean'].mean() + hourly_stats['mean'].std()
        peak_hours = hourly_stats[hourly_stats['mean'] > peak_threshold].index.tolist()
        
        self.analysis_results['hourly_stats'] = hourly_stats
        self.analysis_results['peak_hours'] = peak_hours
        
        fig, ax = plt.subplots(figsize=(14, 7))
        colors = ['red' if hour in peak_hours else 'skyblue' for hour in hourly_stats.index]
        hourly_stats['mean'].plot(kind='bar', ax=ax, color=colors, alpha=0.8, zorder=2)
        ax.axhline(y=peak_threshold, color='red', linestyle='--', linewidth=2, label=f'高峰阈值: {peak_threshold:.3f} T/h')
        ax.set_title(f'{self.building_name} - 每小时平均用水量模式', fontsize=16, fontweight='bold')
        ax.set_xlabel('小时')
        ax.set_ylabel('平均用水量 (T/小时)')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, 'hourly_patterns.png'), dpi=300)
        plt.close(fig)
        print("✓ Hourly patterns analyzed and plot saved.")

    def analyze_weekly_patterns(self):
        print("\nAnalyzing weekly patterns (Weekday vs Weekend)...")
        daily_stats = self.data.groupby(['是否周末', '小时'])['水流量'].mean().unstack(level=0)
        daily_stats.columns = ['工作日', '周末']
        
        self.analysis_results['weekly_stats'] = daily_stats

        fig, ax = plt.subplots(figsize=(14, 7))
        daily_stats.plot(kind='line', marker='o', ax=ax)
        ax.set_title(f'{self.building_name} - 工作日与周末用水模式对比', fontsize=16, fontweight='bold')
        ax.set_xlabel('小时')
        ax.set_ylabel('平均用水量 (T/小时)')
        ax.legend(title='类型')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_folder, 'weekly_patterns.png'), dpi=300)
        plt.close(fig)
        print("✓ Weekly patterns analyzed and plot saved.")

    def perform_clustering(self):
        print("\nPerforming daily pattern clustering...")
        daily_profiles = self.data.pivot_table(index='日期', columns='小时', values='水流量', fill_value=0)
        
        # Find optimal k
        sse = {}
        for k in range(2, 8):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto').fit(daily_profiles)
            sse[k] = kmeans.inertia_
        
        optimal_k = min(sse, key=sse.get)
        self.analysis_results['optimal_k'] = optimal_k

        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init='auto').fit(daily_profiles)
        daily_profiles['cluster'] = kmeans.labels_
        
        self.analysis_results['clustering_results'] = daily_profiles
        
        fig, axes = plt.subplots(optimal_k, 1, figsize=(14, 4 * optimal_k), sharex=True, sharey=True)
        if optimal_k == 1: axes = [axes]
        fig.suptitle(f'{self.building_name} - {optimal_k}种典型日用水模式 (聚类分析)', fontsize=18, fontweight='bold')

        for i in range(optimal_k):
            cluster_data = daily_profiles[daily_profiles['cluster'] == i].drop('cluster', axis=1)
            axes[i].plot(cluster_data.mean(axis=0), label=f'模式 {i+1} (共 {len(cluster_data)} 天)', marker='o')
            axes[i].fill_between(cluster_data.columns, 
                               cluster_data.min(axis=0), 
                               cluster_data.max(axis=0), 
                               alpha=0.2)
            axes[i].set_ylabel('平均用水量 (T/小时)')
            axes[i].legend()
            axes[i].grid(True, linestyle='--', alpha=0.7)
        
        axes[-1].set_xlabel('小时')
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(os.path.join(self.results_folder, 'clustering_patterns.png'), dpi=300)
        plt.close(fig)
        print(f"✓ Clustering complete with {optimal_k} clusters. Plot saved.")

    def generate_report_text(self):
        print("\nGenerating analysis report text...")
        report_lines = []
        report_lines.append(f"用水习惯分析报告 - {self.building_name}")
        report_lines.append("="*50)
        report_lines.append(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Hourly Analysis Summary
        report_lines.append("--- 每小时用水模式分析 ---")
        peak_hours = self.analysis_results.get('peak_hours', [])
        report_lines.append(f"识别出的高峰时段为: {peak_hours}")
        hourly_mean = self.analysis_results.get('hourly_stats', {}).get('mean', pd.Series())
        if not hourly_mean.empty:
            peak_avg = hourly_mean[peak_hours].mean()
            non_peak_avg = hourly_mean[~hourly_mean.index.isin(peak_hours)].mean()
            report_lines.append(f"高峰时段平均用水量: {peak_avg:.3f} T/小时")
            report_lines.append(f"非高峰时段平均用水量: {non_peak_avg:.3f} T/小时")
            report_lines.append(f"用水高峰期的用水量是非高峰期的 {(peak_avg/non_peak_avg):.2f} 倍。\n")
        
        # Weekly Analysis Summary
        report_lines.append("--- 工作日与周末对比 ---")
        weekly_stats = self.analysis_results.get('weekly_stats')
        if weekly_stats is not None:
            weekday_total = weekly_stats['工作日'].sum()
            weekend_total = weekly_stats['周末'].sum()
            report_lines.append(f"日均用水量 (工作日): {weekday_total:.2f} T")
            report_lines.append(f"日均用水量 (周末): {weekend_total:.2f} T")
            if weekend_total > weekday_total:
                report_lines.append("发现周末用水量普遍高于工作日。\n")
            else:
                report_lines.append("发现工作日用水量普遍高于或持平于周末。\n")

        # Clustering Summary
        report_lines.append("--- 典型日用水模式 (聚类分析) ---")
        optimal_k = self.analysis_results.get('optimal_k')
        if optimal_k:
            report_lines.append(f"通过K-Means聚类，将所有用水天分成了 {optimal_k} 种典型模式。")
            clustering_results = self.analysis_results.get('clustering_results')
            cluster_counts = clustering_results['cluster'].value_counts().sort_index()
            for i, count in cluster_counts.items():
                report_lines.append(f"  - 模式 {i+1}: 共出现 {count} 天，占总天数的 {(count/len(clustering_results)*100):.1f}%")
            report_lines.append("详细模式曲线请参见 'clustering_patterns.png' 图表。\n")

        # Recommendations
        report_lines.append("--- 优化建议 ---")
        report_lines.append("1. **增压泵控制**: 建议在高峰时段 ({}) 提前启动或增加增压泵功率，在非高峰时段可考虑降低频率或间歇运行，以节约电能。".format(peak_hours))
        report_lines.append("2. **错峰用水宣传**: 可以在高峰时段前通过公告等形式，鼓励用户（尤其是在用水量大的楼栋）适当错峰用水。")
        report_lines.append("3. **供水系统维护**: 聚类分析出的异常低用量日可能对应节假日或设备故障，可结合实际情况进行核对。")
        
        report_path = os.path.join(self.results_folder, 'analysis_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
        
        print(f"✓ Analysis report text saved to {report_path}")

    def run_complete_analysis(self):
        if not self.load_and_preprocess_data():
            return None, "数据加载或预处理失败"
        
        self.analyze_hourly_patterns()
        self.analyze_weekly_patterns()
        self.perform_clustering()
        self.generate_report_text()
        
        # --- Create a Zip file of all results ---
        zip_path = os.path.join(os.path.dirname(self.results_folder), f"{self.building_name}_analysis_results.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.results_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
        
        print("\n" + "="*50)
        print(f"分析完成！所有结果图表和报告已打包到: {zip_path}")
        print("="*50)
        return zip_path, None


def run_water_habit_analysis(input_file_path: str, output_dir: str, font_path: str) -> (str, str):
    """
    Callable function to run the water habit analysis.

    Args:
        input_file_path (str): Path to the input CSV file.
        output_dir (str): Directory to save the results.
        font_path (str): Path to the TTF font file for matplotlib.

    Returns:
        tuple[str, str]: A tuple containing (path_to_zip_file, error_message).
                         If successful, error_message is None.
                         If failed, path_to_zip_file is None.
    """
    try:
        # Create a specific sub-folder for this analysis run to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_folder = os.path.join(output_dir, f"results_{timestamp}")
        
        analyzer = WaterHabitAnalyzer(
            input_file_path=input_file_path, 
            results_folder=results_folder,
            font_path=font_path
        )
        zip_path, error = analyzer.run_complete_analysis()
        if error:
            return None, error
        return zip_path, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, str(e) 