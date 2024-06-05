from app import db, create_app
from app.models import User
from werkzeug.security import generate_password_hash


def create_superadmin():
    app = create_app()
    with app.app_context():
        superadmin = User(
            name='Andrew Admin',
            email='admin.andrew@gmail.com',
            password=generate_password_hash('supersecretpassword'),
            role='superadmin'
        )
        db.session.add(superadmin)
        db.session.commit()
        print("Superadmin created successfully")


if __name__ == "__main__":
    create_superadmin()
