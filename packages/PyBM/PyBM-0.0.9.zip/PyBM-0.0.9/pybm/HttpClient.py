import requests

class Response:
    def __init__(self, text, status_code):
        self.text = text
        self.status = status_code

    @classmethod
    def init_requests_based(cls, response):
        return cls(response.text, response.status_code)

class Request:
    def __init__(self, url, headers={}, data=None):
        self.url = url
        self.data = data
        self.headers = {}
        for key, value in headers.items():
            self.add_header(key, value)
            
    def add_header(self, key, val):
        self.headers[key.capitalize()] = val

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
    
    def get(self, request):
        r = self.session.get(request.url)
        return Response.init_requests_based(r)

    def cookies(self):
        return self.session.cookies