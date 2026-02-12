
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_interview_status_column():
    print("🔧 Tentative de suppression de la colonne fantôme 'interview_status'...")
    with connection.cursor() as cursor:
        try:
            # Check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'interviews_interview' AND column_name = 'interview_status';
            """)
            result = cursor.fetchone()
            if result:
                print(f"ℹ️ Colonne 'interview_status' trouvée. Suppression en cours...")
                cursor.execute("ALTER TABLE interviews_interview DROP COLUMN interview_status;")
                print("✅ Colonne 'interview_status' supprimée avec succès.")
            else:
                print("ℹ️ Colonne 'interview_status' non trouvée (déjà supprimée ?).")
            
        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")

if __name__ == "__main__":
    fix_interview_status_column()
