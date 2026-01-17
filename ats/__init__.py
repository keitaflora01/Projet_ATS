__version__ = "0.1.0"
__version_info__ = tuple(
    int(num) if num.isdigit() else num
    for num in __version__.replace("-", ".", 1).split(".")
)

# Expose the Celery application at package level so `celery -A ats` can find it.
# The actual Celery app lives in `config/celery.py` (app variable named `app`).
try:
    from config.celery import app as celery  # noqa: E402
    # Common alias used in many projects
    celery = celery
except Exception:
    # Import errors (e.g. missing deps) should not break normal imports of the package.
    celery = None
