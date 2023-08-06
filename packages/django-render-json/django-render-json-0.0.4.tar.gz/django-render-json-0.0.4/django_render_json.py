import sys


def render_json(data):
	import json
	from django.http import HttpResponse

	return HttpResponse(json.dumps(data), mimetype='application/json')


sys.modules[__name__]  = render_json
