import logging
from django.http import HttpResponseNotFound
from django.shortcuts import render

logger = logging.getLogger(__name__)

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            logger.error(f"404 Not Found: {request.path}")
        return response

    def process_exception(self, request, exception):
        logger.error(f"Exception occurred: {exception}", exc_info=True)
        return render(request, '404.html', status=404)
