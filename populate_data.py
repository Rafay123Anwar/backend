import os
import django
import random
from decimal import Decimal

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import FreelancerProfile, ClientProfile, Portfolio
from jobs.models import Category, Job
from proposals.models import Proposal

User = get_user_model()

def create_categories():
    categories = []
    category_names = [
        "Web Development", 
        "Mobile Development", 
        "UI/UX Design", 
        "Content Writing", 
        "Digital Marketing",
        "Data Science",
        "Graphic Design"
    ]
    
    for name in category_names:
        category, created = Category.objects.get_or_create(name=name)
        if created:
            print(f"Created category: {category.name}")
        categories.append(category)
    
    return categories

def create_users():
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'is_email_verified': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"Created admin user: {admin_user.email}")
    
    # Create freelancers
    freelancers = []
    for i in range(1, 6):
        freelancer, created = User.objects.get_or_create(
            email=f'freelancer{i}@example.com',
            defaults={
                'first_name': f'Freelancer{i}',
                'last_name': 'User',
                'user_type': 'freelancer',
                'is_active': True,
                'is_email_verified': True
            }
        )
        if created:
            freelancer.set_password('password123')
            freelancer.save()
            
            # Get or create freelancer profile
            profile, _ = FreelancerProfile.objects.get_or_create(user=freelancer)
            profile.bio = f"I am freelancer {i} with expertise in various skills."
            profile.skills = ["Python", "Django", "JavaScript", "React", "UI/UX Design"][:i+1]
            profile.experience_years = i + 2
            profile.hourly_rate = Decimal(25 + (i * 5))
            profile.wallet_balance = Decimal(100 * i)
            profile.save()
            
            # Create portfolio items
            for j in range(1, 4):
                Portfolio.objects.create(
                    freelancer=profile,
                    title=f"Portfolio Project {j}",
                    description=f"This is a sample project {j} for freelancer {i}.",
                    url=f"https://example.com/portfolio/{i}/{j}"
                )
            
            print(f"Created freelancer: {freelancer.email}")
            freelancers.append(freelancer)
    
    # Create clients
    clients = []
    for i in range(1, 4):
        client, created = User.objects.get_or_create(
            email=f'client{i}@example.com',
            defaults={
                'first_name': f'Client{i}',
                'last_name': 'User',
                'user_type': 'client',
                'is_active': True,
                'is_email_verified': True
            }
        )
        if created:
            client.set_password('password123')
            client.save()
            
            # Get or create client profile
            profile, _ = ClientProfile.objects.get_or_create(user=client)
            profile.company_name = f"Company {i}"
            profile.wallet_balance = Decimal(500 * i)
            profile.save()
            
            print(f"Created client: {client.email}")
            clients.append(client)
    
    return freelancers, clients

def create_jobs(clients, categories):
    jobs = []
    job_titles = [
        "Build a responsive website",
        "Develop a mobile app",
        "Design a logo",
        "Write content for blog",
        "Create a marketing strategy",
        "Develop an e-commerce platform",
        "Design UI for web application",
        "Create a data visualization dashboard",
        "Develop a REST API",
        "Write technical documentation"
    ]
    
    for i, title in enumerate(job_titles):
        client = clients[i % len(clients)]
        category = categories[i % len(categories)]
        
        job, created = Job.objects.get_or_create(
            title=title,
            client=client,
            defaults={
                'description': f"This is a detailed description for the job: {title}. We need an experienced professional to complete this task.",
                'category': category,
                'skills_required': ["Python", "Django", "JavaScript", "React", "UI/UX Design"][:((i % 5) + 1)],
                'budget': Decimal(100 + (i * 50)),
                'job_type': 'fixed' if i % 2 == 0 else 'hourly',
                'status': 'open'
            }
        )
        
        if created:
            print(f"Created job: {job.title}")
            jobs.append(job)
    
    return jobs

def create_proposals(freelancers, jobs):
    proposals = []
    
    for i, job in enumerate(jobs):
        # Each job gets 1-3 proposals
        num_proposals = min(len(freelancers), (i % 3) + 1)
        
        for j in range(num_proposals):
            freelancer = freelancers[j]
            
            # Skip if proposal already exists
            if Proposal.objects.filter(job=job, freelancer=freelancer).exists():
                continue
            
            proposal = Proposal.objects.create(
                job=job,
                freelancer=freelancer,
                cover_letter=f"I am interested in this job and believe I have the skills required. I have {freelancer.freelancer_profile.experience_years} years of experience in this field.",
                bid_amount=Decimal(job.budget * Decimal(0.8 + (j * 0.1))),
                estimated_time=random.randint(3, 15),
                status='pending'
            )
            
            print(f"Created proposal for job '{job.title}' by {freelancer.email}")
            proposals.append(proposal)
    
    return proposals

if __name__ == "__main__":
    print("Populating database with sample data...")
    # Create categories first
    categories = create_categories()
    # Then create users
    freelancers, clients = create_users()
    # Then create jobs with valid category references
    jobs = create_jobs(clients, categories)
    # Finally create proposals
    proposals = create_proposals(freelancers, jobs)
    print("Database population completed!")