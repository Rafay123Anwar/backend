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
        
        # ✅ Ensure FreelancerProfile is created
        profile, profile_created = FreelancerProfile.objects.get_or_create(
            user=freelancer,
            defaults={
                "bio": f"I am freelancer {i} with expertise in various skills.",
                "skills": ["Python", "Django", "JavaScript", "React", "UI/UX Design"][:i+1],
                "experience_years": i + 2,
                "hourly_rate": Decimal(25 + (i * 5)),
                "wallet_balance": Decimal(100 * i)
            }
        )
        
        print(f"Created freelancer: {freelancer.email} (Profile {'Created' if profile_created else 'Exists'})")
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
        
        # ✅ Ensure ClientProfile is created
        profile, profile_created = ClientProfile.objects.get_or_create(
            user=client,
            defaults={"company_name": f"Company {i}", "wallet_balance": Decimal(500 * i)}
        )
        
        print(f"Created client: {client.email} (Profile {'Created' if profile_created else 'Exists'})")
        clients.append(client)

    return freelancers, clients
