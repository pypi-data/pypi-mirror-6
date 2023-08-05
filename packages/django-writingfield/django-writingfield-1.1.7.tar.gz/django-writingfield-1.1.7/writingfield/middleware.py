

class WritingFieldMiddleware(object):

    def process_response(self, request, response):
        if request.META.get('HTTP_X_FROM_WRITINGFIELD') == 'True':

            # for cookies
            response.delete_cookie('messages')

            # for session
            try:
                del(request.session['_messages'])
            except KeyError:
                pass

        return response
