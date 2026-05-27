"""Restablece la contraseña del administrador."""
import argparse

from dotenv import load_dotenv

load_dotenv()

from app import ADMIN_PASSWORD, app, bcrypt
from database import ADMIN_EMAIL
from models import User, db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--password',
        default=ADMIN_PASSWORD,
        help='Nueva contraseña (por defecto: ADMIN_PASSWORD del .env o admin1234)',
    )
    args = parser.parse_args()
    new_password = args.password.strip()

    with app.app_context():
        user = User.query.filter_by(is_admin=True).first()
        if not user:
            user = User(name='Administrador', email=ADMIN_EMAIL, is_admin=True)
            db.session.add(user)
        user.set_password(bcrypt, new_password)
        db.session.commit()

    print('Contraseña de admin actualizada.')
    print(f'  Email panel: {ADMIN_EMAIL}')
    print(f'  Contraseña:  {new_password}')
    print('  URL: http://127.0.0.1:5000/admin/login')


if __name__ == '__main__':
    main()
