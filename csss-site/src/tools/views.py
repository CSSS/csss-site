import base64
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse

from csss.views.context_creation.create_main_context import create_main_context

from .lib.generate_document import CoreChequeReq, Mailed, Pickup, generate_core_cheque_req

# ---------------------
# views


def sample_tool(request):
    return render(request, 'sample_tool.html', create_main_context(request, "more"))


def generate_cheque_req_tool(request):
    return render(request, 'generate_cheque_req.html', create_main_context(request, "more"))


def generate_cheque_req_process(request):
    # debug:
    print("POST: {}\n GET: {}".format(request.POST, request.GET))

    if request.GET["reimburse_method"] == "pickup":
        receive_kind = Pickup(request.GET["pickup_name"], request.GET["pickup_email"])
    else:
        receive_kind = Mailed(
            request.GET["address_is_on_campus"],
            request.GET["address_street"],
            request.GET["address_city_province"],
            request.GET["address_postal_code"])

    cheque_req = CoreChequeReq(
        request_by=request.GET["request_by"],
        requester_position=request.GET["requester_position"],
        request_desc=request.GET["request_desc"],

        payable_to=request.GET["payable_to"],
        amount_cad=float(request.GET["amount_cad"]),
        receive_kind=receive_kind,

        current_date=datetime.strptime(request.GET["date"], '%Y-%m-%d')
    )

    pdf_bytes = generate_core_cheque_req(cheque_req, None, [])

    base64_pdf_bytes = base64.b64encode(pdf_bytes).decode('utf-8')

    response = HttpResponse(base64_pdf_bytes, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="result.pdf"'

    return response
