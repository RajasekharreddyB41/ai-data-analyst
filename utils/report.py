from fpdf import FPDF
import os
import tempfile


class AnalystReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "AI Data Analyst Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_report(profile: dict, formatted_profile: str, chat_history: list, charts: list = None) -> str:
    """Generate a PDF report and return the file path."""

    pdf = AnalystReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Section 1: Dataset Overview
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "1. Dataset Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Rows: {profile['rows']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Columns: {profile['columns']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Column Names: {', '.join(profile['column_names'])}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Numeric stats
    if "stats" in profile:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Numeric Summary:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for col, stat in profile["stats"].items():
            pdf.cell(0, 7, f"  {col}: min={stat['min']}, max={stat['max']}, avg={stat['mean']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Correlations
    if "correlations" in profile and profile["correlations"]:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Interesting Correlations:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for col1, col2, value in profile["correlations"]:
            strength = "strong" if abs(value) >= 0.7 else "moderate"
            pdf.cell(0, 7, f"  {col1} & {col2}: {value} ({strength})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Missing values
    if profile["missing"]:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Missing Values:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for col, pct in profile["missing"].items():
            pdf.cell(0, 7, f"  {col}: {pct}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Section 2: Analysis History
    if chat_history:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "2. Analysis Results", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        for i, chat in enumerate(chat_history, 1):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 8, f"Q{i}: {chat['query']}")
            pdf.ln(2)

            pdf.set_font("Helvetica", "", 10)
            # Clean summary of special characters
            summary = chat.get("summary", "No summary available.")
            summary = summary.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, f"Answer: {summary}")
            pdf.ln(5)

    # Section 3: Charts
    if charts:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "3. Visualizations", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        for i, chart_path in enumerate(charts):
            if os.path.exists(chart_path):
                pdf.image(chart_path, x=10, w=190)
                pdf.ln(10)

    # Save PDF
    temp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(temp_dir, "analysis_report.pdf")
    pdf.output(pdf_path)

    return pdf_path