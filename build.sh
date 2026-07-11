#!/bin/bash
echo "🚀 Building with SQLite..."

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create admin user
python manage.py shell << EOF
from django.contrib.auth import get_user_model
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
    print("✅ Admin user created!")
else:
    print("✅ Admin user already exists.")
EOF

# Collect static files
python manage.py collectstatic --noinput

echo "✅ Build completed!"
