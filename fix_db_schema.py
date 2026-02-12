
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_schema():
    print("🔧 Tentative de correction du schéma de base de données...")
    with connection.cursor() as cursor:
        try:
            # Check current type
            cursor.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'interviews_interview' AND column_name = 'status';
            """)
            result = cursor.fetchone()
            print(f"ℹ️ Type actuel de la colonne 'status': {result[0] if result else 'Inconnu'}")
            
            # Alter column to VARCHAR
            print("RUNNING: ALTER TABLE interviews_interview ALTER COLUMN status TYPE varchar(30);")
            cursor.execute("ALTER TABLE interviews_interview ALTER COLUMN status TYPE varchar(30);")
            print("✅ Schéma corrigé avec succès.")
            
        except Exception as e:
            print(f"❌ Erreur lors de la correction : {e}")

if __name__ == "__main__":
    fix_schema()
