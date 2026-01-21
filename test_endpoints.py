import requests
import json
import os
import random
import string

BASE_URL = "http://localhost:8000"  # Adjust if needed
CV_PATH = "/home/eddy/projects/kieta/Projet_ATS/Fotso_Eddy_CV.pdf"

def get_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def register_user(email, password, role, company_name=None):
    url = f"{BASE_URL}/users/api/register/"
    data = {
        "email": email,
        "password": password,
        "password2": password,
        "role": role
    }
    if company_name:
        data["company_name"] = company_name
    
    print(f"\n--- Registering {role}: {email} ---")
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Response: {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def login_user(email, password):
    url = f"{BASE_URL}/users/api/login/"
    data = {
        "email": email,
        "password": password
    }
    print(f"\n--- Logging in {email} ---")
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def create_job_offer(token, title):
    url = f"{BASE_URL}/jobs/api/offers/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": "This is a test job offer description created by the test script.",
        "job_type": "full_time",
        "contract_type": "cdi",
        "salary_min": 30000,
        "salary_max": 50000,
        "location": "Paris"
    }
    print(f"\n--- Creating Job Offer: {title} ---")
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def submit_application(token, job_id, cv_path):
    url = f"{BASE_URL}/submissions/api/submissions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "job_offer_id": job_id
    }
    
    print(f"\n--- Submitting Application for Job {job_id} ---")
    try:
        with open(cv_path, "rb") as f:
            files = {
                "cv_file": (os.path.basename(cv_path), f, "application/pdf")
            }
            response = requests.post(url, headers=headers, data=data, files=files)
            
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except FileNotFoundError:
        print(f"Error: CV file not found at {cv_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    print("Starting E2E Test Script...")
    
    # 1. Setup Recruiter
    recruiter_email = f"rec_{get_random_string()}@test.com"
    password = "TestPassword123!"
    company_name = f"Company_{get_random_string()}"
    
    reg_response = register_user(recruiter_email, password, "recruiter", company_name)
    if not reg_response or reg_response.status_code != 201:
        print("Aborting: Failed to register recruiter.")
        return

    recruiter_auth = login_user(recruiter_email, password)
    if not recruiter_auth:
        print("Aborting: Failed to login recruiter.")
        return

    recruiter_token = recruiter_auth["access"]
    
    # 2. Create Job
    job_title = f"Developer {get_random_string()}"
    job = create_job_offer(recruiter_token, job_title)
    
    if not job:
        print("Aborting: Failed to create job.")
        return
        
    job_id = job["id"]
    print(f"Job Created Successfully with ID: {job_id}")
    
    # 3. Setup Candidate
    candidate_email = f"cand_{get_random_string()}@test.com"
    reg_response = register_user(candidate_email, password, "candidate")
    if not reg_response or reg_response.status_code != 201:
        print("Aborting: Failed to register candidate.")
        return

    candidate_auth = login_user(candidate_email, password)
    if not candidate_auth:
        print("Aborting: Failed to login candidate.")
        return
        
    candidate_token = candidate_auth["access"]
    
    # 4. Submit Application
    if os.path.exists(CV_PATH):
        submit_application(candidate_token, job_id, CV_PATH)
    else:
        print(f"CV file not found at {CV_PATH}")

if __name__ == "__main__":
    main()
