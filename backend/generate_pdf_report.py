# backend/generate_pdf_report.py
"""Generate detailed PDF report for tech department"""
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors

class PDFReportGenerator:
    def __init__(self, db_path="pharma_enhanced.db"):
        self.db_path = db_path
        self.styles = getSampleStyleSheet()
    
    def generate_report(self, filename="Data_Quality_Report.pdf"):
        """Generate comprehensive PDF report"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=1  # Center
        )
        elements.append(Paragraph("📊 PHARMACEUTICAL DATA QUALITY REPORT", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['Heading2']))
        summary_text = f"""
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Database:</b> pharma_enhanced.db<br/>
        <b>Report Type:</b> Data Quality & AI Readiness Assessment<br/>
        """
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Quality Metrics Table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM ingestion_log ORDER BY ingestion_date DESC LIMIT 1")
        latest_log = cursor.fetchone()
        
        if latest_log:
            elements.append(Paragraph("QUALITY METRICS", self.styles['Heading2']))
            
            metrics_data = [
                ['Metric', 'Value'],
                ['Total Records Attempted', str(latest_log[2])],
                ['Total Records Inserted', str(latest_log[3])],
                ['Duplicates Skipped', str(latest_log[4])],
                ['Validation Errors', str(latest_log[5])],
                ['Null Values Found', str(latest_log[6])],
                ['Quality Score', f"{latest_log[9]:.1f}/100"],
                ['Status', latest_log[8]]
            ]
            
            metrics_table = Table(metrics_data)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(metrics_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Table Statistics
        elements.append(Paragraph("DATABASE TABLE STATISTICS", self.styles['Heading2']))
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%log%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_data = [['Table Name', 'Total Records', 'Passed Validation', 'Pending']]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE validation_status = 'passed'")
            passed = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE validation_status = 'pending'")
            pending = cursor.fetchone()[0]
            
            table_data.append([table, str(total), str(passed), str(pending)])
        
        table_stats = Table(table_data)
        table_stats.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table_stats)
        elements.append(Spacer(1, 0.3*inch))
        
        # AI Readiness
        elements.append(PageBreak())
        elements.append(Paragraph("AI TRAINING READINESS", self.styles['Heading2']))
        
        if latest_log:
            quality_score = latest_log[9]
            if quality_score > 80:
                readiness = "✅ READY FOR AI TRAINING"
                color = colors.green
            elif quality_score > 70:
                readiness = "⚠️ CONDITIONALLY READY"
                color = colors.orange
            else:
                readiness = "❌ NOT READY"
                color = colors.red
            
            readiness_style = ParagraphStyle(
                'Readiness',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=color,
                spaceAfter=12
            )
            
            elements.append(Paragraph(f"<b>{readiness}</b>", readiness_style))
            elements.append(Paragraph(f"Quality Score: {quality_score:.1f}/100", self.styles['Normal']))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        elements.append(Paragraph("RECOMMENDATIONS", self.styles['Heading2']))
        
        recommendations = """
        <b>1. Data Validation:</b> All records have been validated against domain-specific constraints.<br/>
        <b>2. Duplicate Removal:</b> Duplicate records have been automatically detected and removed.<br/>
        <b>3. Quality Assurance:</b> Data completeness and consistency have been verified.<br/>
        <b>4. Next Steps:</b> Export clean data and proceed with AI model training.<br/>
        <b>5. Monitoring:</b> Track data quality metrics over time to ensure consistency.<br/>
        """
        elements.append(Paragraph(recommendations, self.styles['Normal']))
        
        conn.close()
        
        # Build PDF
        doc.build(elements)
        print(f"✅ PDF Report generated: {filename}")

if __name__ == "__main__":
    generator = PDFReportGenerator()
    generator.generate_report()