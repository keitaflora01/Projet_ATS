# ats/utility/email_service.py
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _

def send_interview_invitation(application):
    """
    Envoie un email de félicitations au candidat + invitation.
    """
    subject = _("Félicitations ! Vous passez à l'étape suivante")
    
    candidate_name = application.submission.candidate.get_full_name()
    job_title = application.submission.job_offer.title
    
    message = f"""
    Bonjour {candidate_name},

    Nous avons le plaisir de vous informer que votre candidature pour le poste de "{job_title}" a retenu toute notre attention.
    
    Votre profil correspond aux critères recherchés, et nous souhaitons vous inviter à un entretien.
    
    Vous recevrez prochainement plus de détails sur l'organisation de cet entretien.
    
    Cordialement,
    L'équipe recrutement.
    """
    
    recipient_list = [application.submission.candidate.email]
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print(f"[EMAIL] Invitation envoyée à {recipient_list}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {str(e)}")
        return False
