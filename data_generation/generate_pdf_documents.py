"""
Generate PDF documents for insurance company payer staff
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

def create_policy_guidelines_pdf(output_dir):
    """Create a policy guidelines PDF"""
    filename = os.path.join(output_dir, "Insurance_Policy_Guidelines.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Insurance Policy Guidelines", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Introduction
    story.append(Paragraph("1. Coverage Overview", styles['Heading2']))
    content = """
    Our insurance plans provide comprehensive coverage for medical expenses including hospitalization, 
    outpatient services, prescription drugs, preventive care, and specialist consultations. All plans 
    follow the guidelines established by state and federal regulations.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Pre-authorization Requirements
    story.append(Paragraph("2. Pre-Authorization Requirements", styles['Heading2']))
    content = """
    The following procedures require pre-authorization before services are rendered:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    auth_items = [
        "• Major surgical procedures (excluding emergency)",
        "• MRI and CT scans",
        "• Hospitalization (planned admissions)",
        "• Specialty medications and biologics",
        "• Durable medical equipment over $1,000",
        "• Home health care services",
        "• Physical therapy (beyond initial 6 visits)"
    ]
    
    for item in auth_items:
        story.append(Paragraph(item, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Network Providers
    story.append(Paragraph("3. Network Provider Requirements", styles['Heading2']))
    content = """
    To receive maximum benefits, members must use in-network providers. Out-of-network services 
    may result in higher out-of-pocket costs or claim denials. Emergency services are covered 
    regardless of network status.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Medical Necessity
    story.append(Paragraph("4. Medical Necessity Criteria", styles['Heading2']))
    content = """
    All services must be medically necessary to be covered. Medical necessity means healthcare 
    services that a prudent physician would provide to a patient for the purpose of preventing, 
    diagnosing, or treating an illness, injury, disease, or its symptoms in a manner that is:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    necessity_items = [
        "• In accordance with generally accepted standards of medical practice",
        "• Clinically appropriate in terms of type, frequency, extent, site, and duration",
        "• Not primarily for the convenience of the patient, physician, or other healthcare provider",
        "• Not more costly than alternative services that are at least as likely to produce equivalent results"
    ]
    
    for item in necessity_items:
        story.append(Paragraph(item, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Exclusions
    story.append(Paragraph("5. Common Exclusions", styles['Heading2']))
    content = """
    The following services are typically not covered under standard policies:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    exclusion_items = [
        "• Cosmetic procedures (unless medically necessary)",
        "• Experimental or investigational treatments",
        "• Services not prescribed by a licensed provider",
        "• Self-inflicted injuries (certain circumstances)",
        "• Services outside policy effective dates"
    ]
    
    for item in exclusion_items:
        story.append(Paragraph(item, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

def create_claim_processing_guide_pdf(output_dir):
    """Create a claim processing guide PDF"""
    filename = os.path.join(output_dir, "Claim_Processing_Guide.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Claim Processing Guide", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Claim Submission
    story.append(Paragraph("1. Claim Submission Process", styles['Heading2']))
    content = """
    Claims should be submitted within 90 days of service date. Electronic submission is preferred 
    and results in faster processing times (typically 7-14 days vs 21-30 days for paper claims).
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Required Documentation
    story.append(Paragraph("2. Required Documentation", styles['Heading2']))
    content = """
    All claims must include:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    doc_items = [
        "• Completed claim form (CMS-1500 or UB-04)",
        "• Patient demographics and insurance information",
        "• Provider information and NPI number",
        "• Date(s) of service",
        "• Diagnosis codes (ICD-10)",
        "• Procedure codes (CPT/HCPCS)",
        "• Itemized bill or statement",
        "• Medical records (if requested)"
    ]
    
    for item in doc_items:
        story.append(Paragraph(item, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Processing Timeline
    story.append(Paragraph("3. Processing Timeline", styles['Heading2']))
    
    timeline_data = [
        ['Claim Type', 'Processing Time', 'Payment Time'],
        ['Clean Electronic Claim', '7-14 days', '3-5 days after approval'],
        ['Clean Paper Claim', '21-30 days', '5-7 days after approval'],
        ['Claim Requiring Review', '30-45 days', '5-7 days after approval'],
        ['Appeal/Reconsideration', '45-60 days', '7-10 days after approval']
    ]
    
    table = Table(timeline_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Denial Reasons
    story.append(Paragraph("4. Common Denial Reasons and Resolution", styles['Heading2']))
    content = """
    Understanding why claims are denied helps prevent future rejections:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    denial_data = [
        ['Denial Reason', 'Resolution Action'],
        ['Pre-authorization not obtained', 'Obtain retro-authorization if possible'],
        ['Not medically necessary', 'Submit clinical documentation'],
        ['Out of network provider', 'File out-of-network claim or appeal'],
        ['Service not covered', 'Review policy benefits'],
        ['Insufficient documentation', 'Submit complete medical records'],
        ['Duplicate claim', 'Verify claim status and resubmit if needed'],
        ['Incorrect coding', 'Review and correct CPT/ICD codes']
    ]
    
    denial_table = Table(denial_data, colWidths=[3*inch, 3.5*inch])
    denial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(denial_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Appeals Process
    story.append(Paragraph("5. Appeals Process", styles['Heading2']))
    content = """
    Members and providers have the right to appeal denied claims within 180 days of the denial notice. 
    Appeals should include:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    appeal_items = [
        "• Written appeal letter stating reasons for disagreement",
        "• Supporting clinical documentation",
        "• Relevant medical literature or guidelines",
        "• Provider's clinical rationale"
    ]
    
    for item in appeal_items:
        story.append(Paragraph(item, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

def create_medical_procedures_reference_pdf(output_dir):
    """Create medical procedures reference PDF"""
    filename = os.path.join(output_dir, "Medical_Procedures_Reference.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Medical Procedures Reference Guide", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Cardiology Procedures
    story.append(Paragraph("Cardiology Procedures", styles['Heading2']))
    
    cardio_procedures = [
        ['Procedure', 'CPT Code', 'Pre-Auth Required', 'Avg. Cost Range'],
        ['Echocardiogram', '93306', 'No', '$500-$2,000'],
        ['Cardiac Catheterization', '93458', 'Yes', '$15,000-$50,000'],
        ['Coronary Angioplasty', '92920', 'Yes', '$30,000-$75,000'],
        ['Pacemaker Insertion', '33206', 'Yes', '$25,000-$60,000'],
        ['Stress Test', '93015', 'No', '$300-$1,500']
    ]
    
    cardio_table = Table(cardio_procedures, colWidths=[2*inch, 1.2*inch, 1.5*inch, 1.8*inch])
    cardio_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0504d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(cardio_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Orthopedic Procedures
    story.append(Paragraph("Orthopedic Procedures", styles['Heading2']))
    
    ortho_procedures = [
        ['Procedure', 'CPT Code', 'Pre-Auth Required', 'Avg. Cost Range'],
        ['X-Ray (single view)', '73560', 'No', '$100-$400'],
        ['MRI Scan', '73721', 'Yes', '$1,500-$6,000'],
        ['Knee Arthroscopy', '29881', 'Yes', '$10,000-$25,000'],
        ['Hip Replacement', '27130', 'Yes', '$35,000-$80,000'],
        ['Fracture Treatment', '27508', 'No', '$5,000-$15,000']
    ]
    
    ortho_table = Table(ortho_procedures, colWidths=[2*inch, 1.2*inch, 1.5*inch, 1.8*inch])
    ortho_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f81bd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(ortho_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Diagnostic Imaging
    story.append(Paragraph("Diagnostic Imaging", styles['Heading2']))
    
    imaging_procedures = [
        ['Procedure', 'CPT Code', 'Pre-Auth Required', 'Avg. Cost Range'],
        ['CT Scan (Head)', '70450', 'Yes', '$800-$3,000'],
        ['CT Scan (Chest)', '71250', 'Yes', '$900-$3,500'],
        ['MRI Brain', '70551', 'Yes', '$1,500-$5,000'],
        ['Ultrasound', '76700', 'No', '$300-$1,200'],
        ['PET Scan', '78813', 'Yes', '$3,000-$7,000']
    ]
    
    imaging_table = Table(imaging_procedures, colWidths=[2*inch, 1.2*inch, 1.5*inch, 1.8*inch])
    imaging_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9bbb59')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(imaging_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Notes
    story.append(Paragraph("Important Notes:", styles['Heading3']))
    notes = """
    Cost ranges are estimates and may vary by geographic location, facility type, and patient circumstances. 
    Pre-authorization requirements apply to non-emergency services. Always verify coverage and authorization 
    requirements before scheduling procedures.
    """
    story.append(Paragraph(notes, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

def create_disease_coverage_pdf(output_dir):
    """Create disease coverage information PDF"""
    filename = os.path.join(output_dir, "Disease_Coverage_Information.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Disease Coverage Information", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Diabetes
    story.append(Paragraph("Diabetes Coverage", styles['Heading2']))
    content = """
    Comprehensive coverage for diabetes management includes:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    diabetes_items = [
        "• Blood glucose monitoring supplies (meters, test strips, lancets)",
        "• Insulin and oral diabetes medications",
        "• Insulin pumps and continuous glucose monitors (with pre-authorization)",
        "• Diabetes education and nutritional counseling",
        "• Quarterly HbA1c testing",
        "• Annual diabetic eye exams and foot care",
        "• Coverage for diabetes-related complications"
    ]
    
    for item in diabetes_items:
        story.append(Paragraph(item, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Cardiovascular Disease
    story.append(Paragraph("Cardiovascular Disease Coverage", styles['Heading2']))
    content = """
    Heart disease coverage includes diagnostic, treatment, and preventive services:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    cardio_items = [
        "• Diagnostic testing (ECG, echocardiogram, stress tests)",
        "• Cardiac catheterization and interventional procedures",
        "• Cardiac rehabilitation programs",
        "• Medications (statins, beta-blockers, anticoagulants)",
        "• Pacemakers and defibrillators (with pre-authorization)",
        "• Cardiovascular surgery (bypass, valve replacement)",
        "• Preventive screenings (cholesterol, blood pressure)"
    ]
    
    for item in cardio_items:
        story.append(Paragraph(item, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Cancer
    story.append(Paragraph("Cancer Treatment Coverage", styles['Heading2']))
    content = """
    Comprehensive cancer care coverage includes:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    cancer_items = [
        "• Diagnostic imaging and biopsies",
        "• Surgical oncology procedures",
        "• Chemotherapy and immunotherapy",
        "• Radiation therapy",
        "• Targeted therapy and precision medicine",
        "• Supportive care (pain management, anti-nausea medications)",
        "• Clinical trials (when medically appropriate)",
        "• Oncology rehabilitation services"
    ]
    
    for item in cancer_items:
        story.append(Paragraph(item, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Mental Health
    story.append(Paragraph("Mental Health Coverage", styles['Heading2']))
    content = """
    Mental health services are covered at parity with medical/surgical benefits:
    """
    story.append(Paragraph(content, styles['BodyText']))
    
    mental_items = [
        "• Outpatient therapy (individual, family, group)",
        "• Psychiatric evaluations and medication management",
        "• Inpatient psychiatric hospitalization",
        "• Intensive outpatient programs (IOP)",
        "• Substance abuse treatment and rehabilitation",
        "• Crisis intervention services",
        "• Telehealth mental health services"
    ]
    
    for item in mental_items:
        story.append(Paragraph(item, styles['BodyText']))
    
    doc.build(story)
    print(f"Created: {filename}")

def create_quarterly_report_pdf(output_dir):
    """Create a sample quarterly claims report PDF"""
    filename = os.path.join(output_dir, "Q3_2024_Claims_Report.pdf")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Q3 2024 Claims Report", title_style))
    story.append(Paragraph("July - September 2024", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    content = """
    This report provides an overview of claims activity for Q3 2024. Total claims processed 
    increased by 8% compared to Q2 2024, with a 75% approval rate. Denial rate decreased 
    from 22% to 20%, indicating improved documentation and pre-authorization compliance.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))
    
    # Key Metrics
    story.append(Paragraph("Key Metrics", styles['Heading2']))
    
    metrics_data = [
        ['Metric', 'Q3 2024', 'Q2 2024', 'Change'],
        ['Total Claims Processed', '847', '784', '+8.0%'],
        ['Approved Claims', '635', '580', '+9.5%'],
        ['Denied Claims', '169', '173', '-2.3%'],
        ['Pending Claims', '43', '31', '+38.7%'],
        ['Total Claim Amount', '$8.2M', '$7.6M', '+7.9%'],
        ['Approved Amount', '$6.5M', '$6.1M', '+6.6%'],
        ['Avg Processing Time', '14 days', '16 days', '-12.5%']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Top Denial Reasons
    story.append(Paragraph("Top Denial Reasons", styles['Heading2']))
    
    denial_data = [
        ['Denial Reason', 'Count', 'Percentage'],
        ['Pre-authorization required', '52', '30.8%'],
        ['Not medically necessary', '38', '22.5%'],
        ['Out of network provider', '29', '17.2%'],
        ['Documentation insufficient', '25', '14.8%'],
        ['Service not covered', '15', '8.9%'],
        ['Other', '10', '5.9%']
    ]
    
    denial_table = Table(denial_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
    denial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c0504d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(denial_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    recommendations = [
        "1. Increase provider education on pre-authorization requirements to reduce denial rate",
        "2. Implement enhanced documentation review process before claim submission",
        "3. Expand in-network provider base to reduce out-of-network utilization",
        "4. Continue telehealth initiatives which have shown improved processing efficiency"
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['BodyText']))
        story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    print(f"Created: {filename}")

def main():
    """Generate all PDF documents"""
    print("Generating PDF documents...")
    
    output_dir = 'data/pdf_documents'
    os.makedirs(output_dir, exist_ok=True)
    
    create_policy_guidelines_pdf(output_dir)
    create_claim_processing_guide_pdf(output_dir)
    create_medical_procedures_reference_pdf(output_dir)
    create_disease_coverage_pdf(output_dir)
    create_quarterly_report_pdf(output_dir)
    
    print(f"\n{'='*60}")
    print("PDF GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"All PDF files have been created in: {output_dir}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
