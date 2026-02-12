
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_scheduled_at():
    print("🔧 Tentative de correction de la colonne 'scheduled_at' pour accepter NULL...")
    with connection.cursor() as cursor:
        try:
            # Check is_nullable
            cursor.execute("""
                SELECT is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'interviews_interview' AND column_name = 'scheduled_at';
            """)
            result = cursor.fetchone()
            print(f"ℹ️ 'scheduled_at' nullable actuel: {result[0] if result else 'Inconnu'}")
            
            # Alter column to DROP NOT NULL
            print("RUNNING: ALTER TABLE interviews_interview ALTER COLUMN scheduled_at DROP NOT NULL;")
            cursor.execute("ALTER TABLE interviews_interview ALTER COLUMN scheduled_at DROP NOT NULL;")
            print("✅ Colonne 'scheduled_at' corrigée avec succès.")
            
        except Exception as e:
            print(f"❌ Erreur lors de la correction : {e}")

if __name__ == "__main__":
    fix_scheduled_at()
