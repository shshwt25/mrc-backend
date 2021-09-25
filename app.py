from services.server import APP

port = 5011

if __name__ == '__main__':
    from wsgiref import simple_server
    httpd = simple_server.make_server('0.0.0.0', port, APP)
    httpd.serve_forever()
