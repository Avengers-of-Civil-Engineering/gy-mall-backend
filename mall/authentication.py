from rest_framework.authentication import SessionAuthentication


class MySessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return None
