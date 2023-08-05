from flask.app import Flask, setupmethod


@setupmethod
def urls(self, patterns):
    """A customized function that separates urls and view functions.
    Usage:
        app.urls([
                ('/', home),
                ('/hello', hello)
                ])
        :param patterns: the url patterns grouped together. Each pattern is
                         written as (rule, view_func[, **options])
        """
    for pattern in patterns:
        print(pattern)
        try:
            options = pattern[2]
            endpoint = pattern[2].pop('endpoint', None)
        except IndexError:
            options = {}
            endpoint = None
        self.add_url_rule(pattern[0], endpoint, pattern[1], **options)


def get(self, rule, **options):
    "A customized decorator that directly provide route for GET method."
    options['methods'].append('GET')
    return self.route(rule, **options)


def post(self, rule, **options):
    "A customized decorator that directly provide route for POST method."
    options['methods'].append('POST')
    return self.route(rule, **options)


def head(self, rule, **options):
    "A customized decorator that directly provide route for HEAD method."
    options['methods'].append('HEAD')
    return self.route(rule, **options)


def put(self, rule, **options):
    "A customized decorator that directly provide route for PUT method."
    options['methods'].append('PUT')
    return self.route(rule, **options)


def delete(self, rule, **options):
    "A customized decorator that directly provide route for DELETE method."
    options['methods'].append('DELETE')
    return self.route(rule, **options)


def options(self, rule, **options):
    "A customized decorator that directly provide route for OPTIONS method."
    options['methods'].append('OPTIONS')
    return self.route(rule, **options)

Flask.urls = urls
Flask.get = get
Flask.post = post
Flask.head = head
Flask.put = put
Flask.delete = delete
Flask.options = options
