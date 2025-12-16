"""Adapters placeholder module.

Allauth integration has been removed to make the backend API-only. Keep
this module as a place to implement account adapters if/when you reintroduce
such integrations. For now it provides simple no-op placeholders.
"""


def placeholder_adapter(*args, **kwargs):
    """Return None; implement adapter logic here if needed."""
    return None


class AccountAdapter:
    """Minimal AccountAdapter placeholder for django-allauth.

    This is intentionally minimal: it exists so that `import_attribute`
    (used by allauth during system checks) can resolve the class. If you
    reintroduce allauth integrations later, replace this with a full
    adapter that inherits from `allauth.account.adapter.DefaultAccountAdapter`.
    """

    def __init__(self, *args, **kwargs):
        pass


class SocialAccountAdapter:
    """Minimal SocialAccountAdapter placeholder for django-allauth.

    See notes in `AccountAdapter` above.
    """

    def __init__(self, *args, **kwargs):
        pass
