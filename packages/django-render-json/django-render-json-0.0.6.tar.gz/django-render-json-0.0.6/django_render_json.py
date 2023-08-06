import sys


def render_json(data, mimetype='applicaction/json'):
	import json
	from django.http import HttpResponse

	return HttpResponse(json.dumps(data), mimetype=mimetype)


sys.modules[__name__]  = render_json
