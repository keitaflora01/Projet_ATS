
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_submission_id_column():
    print("🔧 Tentative de suppression de la colonne fantôme 'submission_id'...")
    with connection.cursor() as cursor:
        try:
            # Check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'interviews_interview' AND column_name = 'submission_id';
            """)
            result = cursor.fetchone()
            if result:
                print(f"ℹ️ Colonne 'submission_id' trouvée. Suppression en cours...")
                cursor.execute("ALTER TABLE interviews_interview DROP COLUMN submission_id;")
                print("✅ Colonne 'submission_id' supprimée avec succès.")
            else:
                print("ℹ️ Colonne 'submission_id' non trouvée (déjà supprimée ?).")
            
        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")

if __name__ == "__main__":
    fix_submission_id_column()
