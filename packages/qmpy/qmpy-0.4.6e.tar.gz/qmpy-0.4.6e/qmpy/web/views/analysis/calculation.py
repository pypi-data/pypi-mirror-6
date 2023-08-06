from django.shortcuts import render_to_response
from django.template import RequestContext

from qmpy.models import Calculation

def calculation_view(request, calculation_id):
    calculation = Calculation.objects.get(pk=calculation_id)
    data = {'calculation':calculation}
    if not calculation.dos is None:
        data['dos'] = calculation.dos.plot.get_flot_script()
    return render_to_response('analysis/calculation.html', 
            data, RequestContext(request))
