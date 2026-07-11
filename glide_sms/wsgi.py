import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glide_sms.settings')

# Run migrations and create admin on startup
try:
    from django.core.management import call_command
    from django.contrib.auth import get_user_model
    from django.db import connection
    
    print("📦 Checking database...")
    
    # Check if tables exist
    with connection.cursor() as cursor:
        # Check if core_user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_user';")
        table_exists = cursor.fetchone()
    
    if not table_exists:
        print("🗄️ Creating migrations and running them...")
        call_command('makemigrations', 'core', interactive=False, verbosity=0)
        call_command('makemigrations', interactive=False, verbosity=0)
        call_command('migrate', interactive=False, verbosity=0)
        print("✅ Migrations completed!")
    else:
        print("✅ Database already exists.")
    
    # Create admin user
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@glide-erp.com',
            password='admin123',
            user_type='super_admin',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Admin user created: admin / admin123")
    else:
        print("✅ Admin user already exists.")
        
except Exception as e:
    print(f"⚠️ Database setup warning: {e}")

application = get_wsgi_application()
