"""
Crear o reiniciar la base de datos de productos y usuarios.

Uso:
  python init_db.py           # crea tablas y datos si no existen
  python init_db.py --reset   # borra todo y vuelve a cargar
"""
import argparse

from dotenv import load_dotenv

load_dotenv()

from app import app, bcrypt
from database import init_database
# models importados vía app


def main():
    parser = argparse.ArgumentParser(description='Inicializar base de datos Pedro Joyas')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Borra todas las tablas y vuelve a crear productos y admin',
    )
    parser.add_argument(
        '--sync-products',
        action='store_true',
        help='Reemplaza el catálogo con INITIAL_PRODUCTS (mantiene usuarios y pedidos)',
    )
    args = parser.parse_args()

    with app.app_context():
        result = init_database(
            bcrypt,
            reset=args.reset,
            sync_products=args.sync_products,
        )

    print('Base de datos lista.')
    print(f"  Archivo: jewelry_store.db")
    print(f"  Usuarios: {result['users']}")
    print(f"  Productos: {result['products']}")
    print(f"  Variantes (talles): {result['variants']}")

    if result['products_seeded']:
        print(f"  -> Se cargaron {result['products_seeded']} productos de ejemplo.")
    if result['admin_seeded']:
        print('  -> Usuario admin creado: admin@pedrojoyas.com')
        print('     Contraseña: la de ADMIN_PASSWORD en .env (por defecto admin1234)')

    if args.reset:
        print('  (Base reiniciada con --reset)')
    if args.sync_products:
        print('  (Catálogo actualizado con --sync-products)')


if __name__ == '__main__':
    main()
