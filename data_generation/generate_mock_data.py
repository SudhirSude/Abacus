"""
Generate synthetic insurance claims data for RAG-powered claims query assistant
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import csv

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Define data parameters
NUM_CLAIMS = 3000
NUM_PATIENTS = 1000
NUM_DOCTORS = 200

# Data options
SPECIALTIES = [
    'Cardiology', 'Orthopedics', 'Neurology', 'Oncology', 'Pediatrics',
    'Dermatology', 'Psychiatry', 'Radiology', 'Anesthesiology', 'Emergency Medicine',
    'Family Medicine', 'Internal Medicine', 'Endocrinology', 'Gastroenterology', 'Nephrology'
]

DISEASES = [
    'Diabetes Type 2', 'Hypertension', 'Coronary Artery Disease', 'Asthma', 'COPD',
    'Rheumatoid Arthritis', 'Osteoarthritis', 'Depression', 'Anxiety Disorder', 'Migraine',
    'Pneumonia', 'Urinary Tract Infection', 'Acute Bronchitis', 'Fracture', 'Laceration',
    'Gastroesophageal Reflux', 'Hyperlipidemia', 'Chronic Kidney Disease', 'Cancer',
    'Stroke', 'Acute Myocardial Infarction', 'Congestive Heart Failure', 'Sepsis',
    'Appendicitis', 'Gallstones', 'Herniated Disc', 'Fibromyalgia', 'Psoriasis'
]

PROCEDURES = [
    'Office Visit', 'Lab Tests', 'X-Ray', 'MRI Scan', 'CT Scan', 'Ultrasound',
    'ECG', 'Blood Work', 'Physical Therapy', 'Surgery - Minor', 'Surgery - Major',
    'Emergency Room Visit', 'Hospitalization', 'Chemotherapy', 'Radiation Therapy',
    'Dialysis', 'Endoscopy', 'Colonoscopy', 'Biopsy', 'Vaccination'
]

CLAIM_STATUSES = ['Approved', 'Denied', 'Pending', 'Partially Approved']

DENIAL_REASONS = [
    'Pre-authorization required', 'Not medically necessary', 'Out of network provider',
    'Service not covered', 'Documentation insufficient', 'Duplicate claim',
    'Exceeded benefit limit', 'Procedure not approved', 'Missing information',
    'Experimental treatment', 'Pre-existing condition exclusion', 'Policy lapsed',
    'Incorrect coding', 'Service outside coverage period'
]

INSURANCE_PLANS = [
    'Premium Plus', 'Gold Standard', 'Silver Care', 'Bronze Basic', 
    'Platinum Elite', 'Family Wellness', 'Senior Care', 'Young Adult Plan'
]

FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Barbara', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores'
]

def generate_patients(num_patients):
    """Generate patient data"""
    patients = []
    for i in range(num_patients):
        patient_id = f"PAT{str(i+1).zfill(6)}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        age = random.randint(18, 85)
        gender = random.choice(['Male', 'Female', 'Other'])
        state = random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'])
        insurance_plan = random.choice(INSURANCE_PLANS)
        
        patients.append({
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}",
            'age': age,
            'gender': gender,
            'state': state,
            'insurance_plan': insurance_plan
        })
    
    return pd.DataFrame(patients)

def generate_doctors(num_doctors):
    """Generate doctor data"""
    doctors = []
    for i in range(num_doctors):
        doctor_id = f"DOC{str(i+1).zfill(5)}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        specialty = random.choice(SPECIALTIES)
        network_status = np.random.choice(['In-Network', 'Out-of-Network'], p=[0.85, 0.15])
        hospital = f"{random.choice(['St. Mary', 'General', 'Memorial', 'Regional', 'Central'])} Hospital"
        
        doctors.append({
            'doctor_id': doctor_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"Dr. {first_name} {last_name}",
            'specialty': specialty,
            'network_status': network_status,
            'hospital': hospital
        })
    
    return pd.DataFrame(doctors)

def generate_claims(num_claims, patients_df, doctors_df):
    """Generate claims data"""
    claims = []
    
    # Date range: last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    for i in range(num_claims):
        claim_id = f"CLM{str(i+1).zfill(7)}"
        
        # Random date within range
        days_offset = random.randint(0, 730)
        claim_date = start_date + timedelta(days=days_offset)
        service_date = claim_date - timedelta(days=random.randint(0, 30))
        
        # Random patient and doctor
        patient = patients_df.iloc[random.randint(0, len(patients_df)-1)]
        doctor = doctors_df.iloc[random.randint(0, len(doctors_df)-1)]
        
        # Claim details
        disease = random.choice(DISEASES)
        procedure = random.choice(PROCEDURES)
        
        # Generate claim amount based on procedure type
        if 'Surgery - Major' in procedure or 'Hospitalization' in procedure:
            claim_amount = round(random.uniform(50000, 200000), 2)
        elif 'Surgery - Minor' in procedure or 'Emergency' in procedure:
            claim_amount = round(random.uniform(10000, 50000), 2)
        elif 'MRI' in procedure or 'CT Scan' in procedure:
            claim_amount = round(random.uniform(2000, 8000), 2)
        else:
            claim_amount = round(random.uniform(100, 5000), 2)
        
        # Determine claim status with realistic probabilities
        status_weights = [0.65, 0.20, 0.10, 0.05]  # Approved, Denied, Pending, Partially Approved
        claim_status = random.choices(CLAIM_STATUSES, weights=status_weights)[0]
        
        # Denial reason for denied claims
        denial_reason = random.choice(DENIAL_REASONS) if claim_status == 'Denied' else 'N/A'
        
        # Approved amount
        if claim_status == 'Approved':
            approved_amount = claim_amount
        elif claim_status == 'Partially Approved':
            approved_amount = round(claim_amount * random.uniform(0.4, 0.9), 2)
        else:
            approved_amount = 0.0
        
        # Processing time
        processing_days = random.randint(1, 60)
        processed_date = claim_date + timedelta(days=processing_days) if claim_status != 'Pending' else None
        
        # Quarter and year
        quarter = f"Q{(claim_date.month-1)//3 + 1}"
        year = claim_date.year
        
        claims.append({
            'claim_id': claim_id,
            'patient_id': patient['patient_id'],
            'patient_name': patient['full_name'],
            'patient_age': patient['age'],
            'patient_gender': patient['gender'],
            'patient_state': patient['state'],
            'insurance_plan': patient['insurance_plan'],
            'doctor_id': doctor['doctor_id'],
            'doctor_name': doctor['full_name'],
            'doctor_specialty': doctor['specialty'],
            'network_status': doctor['network_status'],
            'hospital': doctor['hospital'],
            'disease': disease,
            'procedure': procedure,
            'service_date': service_date.strftime('%Y-%m-%d'),
            'claim_date': claim_date.strftime('%Y-%m-%d'),
            'processed_date': processed_date.strftime('%Y-%m-%d') if processed_date else 'N/A',
            'claim_amount': claim_amount,
            'approved_amount': approved_amount,
            'claim_status': claim_status,
            'denial_reason': denial_reason,
            'processing_days': processing_days if claim_status != 'Pending' else 'N/A',
            'quarter': quarter,
            'year': year
        })
    
    return pd.DataFrame(claims)

def main():
    """Generate all datasets"""
    print("Generating synthetic insurance claims data...")
    
    # Generate data
    print(f"Generating {NUM_PATIENTS} patients...")
    patients_df = generate_patients(NUM_PATIENTS)
    
    print(f"Generating {NUM_DOCTORS} doctors...")
    doctors_df = generate_doctors(NUM_DOCTORS)
    
    print(f"Generating {NUM_CLAIMS} claims...")
    claims_df = generate_claims(NUM_CLAIMS, patients_df, doctors_df)
    
    # Save to CSV files
    output_dir = 'data'
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    patients_df.to_csv(f'{output_dir}/patients.csv', index=False)
    print(f"Saved {len(patients_df)} patients to {output_dir}/patients.csv")
    
    doctors_df.to_csv(f'{output_dir}/doctors.csv', index=False)
    print(f"Saved {len(doctors_df)} doctors to {output_dir}/doctors.csv")
    
    claims_df.to_csv(f'{output_dir}/claims.csv', index=False)
    print(f"Saved {len(claims_df)} claims to {output_dir}/claims.csv")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("DATA GENERATION SUMMARY")
    print("="*60)
    print(f"Total Claims: {len(claims_df)}")
    print(f"Total Patients: {len(patients_df)}")
    print(f"Total Doctors: {len(doctors_df)}")
    print("\nClaim Status Distribution:")
    print(claims_df['claim_status'].value_counts())
    print("\nTop 5 Diseases:")
    print(claims_df['disease'].value_counts().head())
    print("\nTop 5 Procedures:")
    print(claims_df['procedure'].value_counts().head())
    print("\nDate Range:")
    print(f"From: {claims_df['claim_date'].min()}")
    print(f"To: {claims_df['claim_date'].max()}")
    print("\nTotal Claim Amount: ${:,.2f}".format(claims_df['claim_amount'].sum()))
    print("Total Approved Amount: ${:,.2f}".format(claims_df['approved_amount'].sum()))
    print("="*60)

if __name__ == "__main__":
    main()
