from models import set_current_user, clear_current_user


class CurrentUserMiddleware(object):

    def process_request(self, request):
        set_current_user(getattr(request, 'user', None))

    def process_response(self, request, response):
        clear_current_user()
        return response

    def process_exception(self, request, exception):
        clear_current_user()
