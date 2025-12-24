def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    get_params = environ.get('QUERY_STRING', '')

    try:
        size = int(environ.get('CONTENT_LENGTH', 0))
        post_data = environ['wsgi.input'].read(size).decode() if size > 0 else ''
    except:
        post_data = ''

    response_body = f"Method: {method}\nGET: {get_params}\nPOST: {post_data}"
    response_body = response_body.encode('utf-8')

    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [response_body]
