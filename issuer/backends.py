from django_cas_ng.backends import CASBackend


class CASAdminOnlyBackend(CASBackend):
    def user_can_authenticate(self, user):
        if user.is_staff:
            return True
        return False
