import os
from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        # Add font that supports unicode characters
        # The font file must be available. We'll need to add one to the project.
        try:
            self.add_font('simsun', '', 'simsun.ttf', uni=True)
            self.set_font('simsun', '', 12)
        except RuntimeError:
            # Fallback to a standard font if the custom font is not found
            self.set_font('Arial', 'B', 12)
        
        self.cell(0, 10, '热水系统智能分析报告', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font('simsun', '', 8)
        except RuntimeError:
            self.set_font('Arial', 'I', 8)
        
        page_number = f'第 {self.page_no()} 页'
        self.cell(0, 10, page_number, 0, 0, 'C')

class ReportGenerator:
    def __init__(self, title, description):
        self.pdf = PDF()
        # Add the font file to the FPDF font cache
        # This is a bit of a workaround. A better solution might involve managing fonts more centrally.
        font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'simsun.ttf')
        if not os.path.exists(font_path):
            print(f"Warning: Font file not found at {font_path}. Chinese characters may not render correctly.")
        else:
             self.pdf.add_font('simsun', '', font_path, uni=True)

        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.set_font("simsun", size=24)
        self.pdf.cell(0, 15, title, 0, 1, 'C')
        self.pdf.ln(5)

        self.pdf.set_font("simsun", size=12)
        self.pdf.multi_cell(0, 10, description)
        self.pdf.ln(10)

    def add_analysis_section(self, task):
        self.pdf.set_font("simsun", 'B', 16)
        self.pdf.cell(0, 10, f"分析任务: {task.task_name}", 0, 1)
        self.pdf.ln(5)

        self.pdf.set_font("simsun", '', 12)
        self.pdf.multi_cell(0, 8, f"任务类型: {task.task_type}")
        self.pdf.multi_cell(0, 8, f"创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        self.pdf.multi_cell(0, 8, f"所用参数: {task.parameters}")
        self.pdf.ln(5)

        if task.result:
            plot_path = task.result.get('plot_path')
            if plot_path and os.path.exists(plot_path):
                self.pdf.set_font("simsun", 'B', 14)
                self.pdf.cell(0, 10, "分析图表", 0, 1)
                self.pdf.image(plot_path, x=None, y=None, w=self.pdf.w - 40) # w = page width - 40 margin
                self.pdf.ln(5)

            self.pdf.set_font("simsun", 'B', 14)
            self.pdf.cell(0, 10, "分析结果摘要", 0, 1)
            self.pdf.set_font("simsun", '', 10)
            
            # Pretty print the JSON result
            result_str = str(task.result)
            self.pdf.multi_cell(0, 5, result_str)
            self.pdf.ln(10)

    def generate(self):
        return self.pdf.output(dest='S').encode('latin-1') 