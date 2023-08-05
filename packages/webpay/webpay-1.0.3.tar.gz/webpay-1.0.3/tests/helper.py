def mock_api(path, file_path, query=None, data=None):
    from httmock import urlmatch, response
    import json

    @urlmatch(scheme='https', netloc='api.webpay.jp', path='/v1' + path)
    def webpay_api_mock(url, request):
        assert query is None or url.query == query
        assert data is None or json.loads(request.body) == data

        from os import path
        import codecs
        dump = path.dirname(path.abspath(__file__)) + '/mock/' + file_path
        file = codecs.open(dump, 'r', 'utf-8')
        lines = file.readlines()
        file.close

        status = 0
        headers = {}
        body = ''
        body_started = False

        for i in range(len(lines)):
            line = lines[i]
            if i == 0:
                status = int(line.split(' ')[1])
            elif body_started:
                body += line
            elif (line.strip() == ''):
                body_started = True
            else:
                key, value = line.split(':', 1)
                headers[key] = value.strip()

        return response(status,
                        content=body.encode('utf-8'),
                        headers=headers,
                        request=request)
    return webpay_api_mock
