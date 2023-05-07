from dataclasses import dataclass
from datetime import datetime

#from util import *

from pypdf import PdfReader, PdfWriter, PdfReader
from pypdf.generic import NameObject
from reportlab.pdfgen import canvas

# definitions:
# - Cheque Requisison (or Cheque-Req for short) is a document that requests money from the sfss
# - 

# ------------------------
# globals

# https://sfss.ca/wp-content/uploads/2022/09/Cheque-Requisition-Form-Pick-Up-2022-1P.pdf
small_text_logo = "logo-text-smaller.png"
cheque_req_form_pickup = "Cheque-Requisition-Form-Pick-Up-2022-1P.pdf"
cheque_req_form_mailed = "..."

# ------------------------
# structs

#NOTE: these are pretty much just C-style structs
# TODO: have example values for all dataclasses

@dataclass
class Pickup:
    pickup_by: str          
    pickup_email: str   

@dataclass
class Mailed:
    mail_off_campus: bool
    street_address: str
    city_province: str
    postal_code: str

@dataclass
class CoreChequeReq:
    requested_by: str
    requester_position: str 
    request_desc: str 

    payable_to: str         
    amount_cad: float       
    receive_kind: Pickup | Mailed 

    current_date: datetime 

@dataclass
class ReceiptInfo:
    paid_by: str 
    location: str  
    amount_cad: float 

# ------------------------
# functions

# generate cheque req from core
# meeting_minutes: str is the prefix for the meeting minutes of the form: "yyyy-mm-dd"
def generate_core_cheque_req(data: CoreChequeReq, meeting_minutes: str, receipts: list[ReceiptInfo], out_file_name: str, include_auto_desc: bool = True, watermark_active: bool = True):
    reader = PdfReader(cheque_req_form_pickup)
    assert len(reader.pages) == 1

    page = reader.pages[0]

    # TODO: automatically generate a description given info about receipts
    # TODO: automatically include attached meeting minutes in the cheque-req -> do a search; look for person's name & reciept costs
    # TODO: in the web tool, have a link to this script's source, and an existing filled out form (or something like that)

    relevant_fields = {
        'Today s Date': data.current_date.strftime("%B %#d, %Y"),
        'Cheque Payable To print legibly': data.payable_to, 
        'In The Amount Of': "${0:.2f}".format(data.amount_cad), 
        'Describe the request andor provide additional information if necessary': data.request_desc, 

        'Requested By': data.requested_by, 
        'Position': data.requester_position,
    }

    # contextual fields 
    if isinstance(data.receive_kind, Pickup):
        relevant_fields['Picked up by'] = data.receive_kind.pickup_by
        relevant_fields['Email'] = data.receive_kind.pickup_email
    elif isinstance(data.receive_kind, Mailed):
        relevant_fields['Street Address'] = data.receive_kind.street_address
        relevant_fields['City, Province'] = data.receive_kind.city_province
        relevant_fields['Postal Code'] = data.receive_kind.postal_code
        
        # check boxes are not easy, so just update them in the reader's page
        found_check_box_1 = False
        found_check_box_3 = False
        if "/Annots" in page:
            for annotation in page["/Annots"]:
                annotation_obj = annotation.get_object()
                annotation_type = annotation_obj['/T']
                if annotation_type == "Check Box1":
                    found_check_box_1 = True 
                elif annotation_type == "Check Box3":
                    found_check_box_3 = True
                
                if annotation_type == "Check Box1" and data.receive_kind.mail_off_campus or \
                   annotation_type == "Check Box3" and not data.receive_kind.mail_off_campus:
                    annotation_obj.update({
                        NameObject("/V"): NameObject("/Yes"),
                        NameObject("/AS"): NameObject("/Yes")
                    })
        else:
            raise KeyError("pdf has no checkboxes; something is wrong!")
        
        if not found_check_box_1 or not found_check_box_3:
            raise KeyError("could not find checkboxes; pdf may be malformed")
    else:
        raise AssertionError("Invalid value {}; exhaustive case".format(data.receive_kind))

    # ------------------------
    # validation

    fields = reader.get_form_text_fields()
    for key in relevant_fields.keys():
        if not key in fields:
            raise KeyError("pdf form did not have neccesary key")

    # ------------------------
    # final writing

    c = canvas.Canvas('tmp/watermark.pdf')
    c.drawString(335, 702, "Computing Science Student Society")
    if watermark_active: c.drawImage(small_text_logo, 429, 725, 848 / 6, 174 / 6)
    c.save()

    csss_text_logo = PdfReader(open('tmp/watermark.pdf', "rb"))
    page.merge_page(csss_text_logo.pages[0])
    
    writer = PdfWriter()
    writer.add_page(page)
    writer.update_page_form_field_values(writer.pages[0], relevant_fields)

    with open(out_file_name, "wb") as output_stream:
        writer.write(output_stream)


# generate cheque req from grant
def generate_grant_cheque_req():
    pass

# generate invoice
def generate_invoice():
    pass

# generate travel & conference funding request
def generate_travel_conference_funding_req():
    pass

# search through motions from the past n years for keywords
def search_motions(keyword, threshold=0, nyears=2):
    # 1. fetch all the pdfs (report how that's going...)
    # pypdf to read stuff
    
    # 2. parse them for text
    # TODO: check if pip install thefuzz[speedup] actually helps & by how much?
    # thefuzz to match text with keyword

    # 3. return all matches over a certain similarity threshold
    pass

# ------------------------
# testing

if __name__ == "__main__":
    cheque_req = CoreChequeReq(
        requested_by = "Gabe", 
        requester_position = "Treasurer", 
        request_desc = "Something shall be requested from core!", 
        
        payable_to = "payee", 
        amount_cad = 10.00, 
        #receive_kind = Pickup("picker upper", "pickup@email.com"), 
        receive_kind = Mailed(True, "address", "city", "A2C4E6"), 

        current_date = datetime.now()
    )
    
    print(cheque_req)
    generate_core_cheque_req(cheque_req, "2022-02-27", [], "tmp_core_cheque_req.pdf")
