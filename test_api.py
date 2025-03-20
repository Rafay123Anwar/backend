import requests
import json

BASE_URL = "http://localhost:8000/api"
ACCESS_TOKEN = None
REFRESH_TOKEN = None

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("-" * 50)

def register_user():
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    print("Registering a new freelancer...")
    url = f"{BASE_URL}/auth/register/"
    data = {
        "email": "test.freelancer@example.com",
        "password": "StrongPassword123!",
        "password2": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "Freelancer",
        "user_type": "freelancer"
    }
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 201:
        ACCESS_TOKEN = response.json().get("access")
        REFRESH_TOKEN = response.json().get("refresh")
        print("Registration successful!")
    else:
        print("Registration failed!")

def login():
    global ACCESS_TOKEN, REFRESH_TOKEN
    
    print("Logging in...")
    url = f"{BASE_URL}/auth/login/"
    data = {
        "email": "freelancer1@example.com",
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print_response(response)
    
    if response.status_code == 200:
        ACCESS_TOKEN = response.json().get("access")
        REFRESH_TOKEN = response.json().get("refresh")
        print("Login successful!")
    else:
        print("Login failed!")

def get_freelancer_profile():
    print("Getting freelancer profile...")
    url = f"{BASE_URL}/auth/freelancer/profile/"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def get_jobs():
    print("Getting jobs...")
    url = f"{BASE_URL}/jobs/"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def get_job_details(job_id=1):
    print(f"Getting job details for job {job_id}...")
    url = f"{BASE_URL}/jobs/{job_id}/"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def create_proposal(job_id=1):
    print(f"Creating proposal for job {job_id}...")
    url = f"{BASE_URL}/proposals/job/{job_id}/"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "cover_letter": "I am very interested in this job and have extensive experience with the required skills.",
        "bid_amount": 90.00,
        "estimated_time": 7
    }
    response = requests.post(url, headers=headers, json=data)
    print_response(response)

def get_my_proposals():
    print("Getting my proposals...")
    url = f"{BASE_URL}/proposals/my/"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    print_response(response)

def main():
    # First, login to get access token
    register_user()
    login()
    
    if ACCESS_TOKEN:
        # Test various API endpoints
        get_freelancer_profile()
        get_jobs()
        get_job_details()
        create_proposal()
        get_my_proposals()
    else:
        print("Cannot proceed without access token!")

if __name__ == "__main__":
    main()
