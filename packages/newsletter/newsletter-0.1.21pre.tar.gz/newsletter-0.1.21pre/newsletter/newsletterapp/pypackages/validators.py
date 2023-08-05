# you can place your validation functions in there.

def myvalidationfunc(kwargs):
    return kwargs.get('url', '').startwith('http://localhost')
