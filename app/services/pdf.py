import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from app.models.incidents import Incident

field_coords = {
    # Top section
    "person_involved": (278, 103),
    "age": (728, 103),
    "phone_number": (228, 129),
    "guest_of": (528, 129),
    "address": (228, 154),
    "parent_guardian": (328, 180),
    "date_of_incident": (228, 232),
    "time_of_incident": (478, 232),
    "facility_name": (278, 258),
    "incident_address": (278, 284),
    "employee": (178, 309),
    "security_contacted": (398, 309),
    "called_911": (578, 309),
    "ambulance": (428, 335),
    "ambulance_where": (278, 360),
    "type_of_incident": (272, 401),

    # Injury types
    "injury_splinter": (87, 614),
    "injury_burn": (231, 614),
    "injury_heat_related": (339, 614),
    "injury_bruise": (87, 644),
    "injury_dental": (231, 644),
    "injury_head_neck_spinal": (339, 644),
    "injury_bite": (87, 673),
    "injury_stroke": (231, 673),
    "injury_choking": (339, 673),
    "injury_cut_scrape": (87, 702),
    "injury_heart_attack": (231, 702),
    "injury_other": (489, 702),

    # Body parts
    "body_eyes_ears_face": None,   # to be marked visually (similar coords extraction)
    "body_neck_shoulders": None,
    "body_arms_elbows": None,
    "body_hips_legs_knees": None,
    "body_wrists_hands_fingers": None,
    "body_ankles_feet_toes": None,
    "body_back": None,
    "body_head": None,
    "body_internal_organs": None,
    "body_other": (489, 702),  # shared with injury section "Other"

    # Detailed account
    "detailed_account": (100, 420),

    # Footer
    "employee_completing": (420, 170),
    "date_of_report": (380, 150),
    "witness": (280, 130),
    "witness_phone": (630, 130)
}

TEMPLATE_PDF = "./app/templates/Fillable Blank Incident Report (2)[35].pdf"
OUTPUT_DIR = "./app/tmp"

field_coords = {
    "person_involved_name": (278, 103),
    "person_involved_age": (728, 103),
    "person_involved_phone_number": (228, 129),
    "person_involved_guest_of": (528, 129),
    "person_involved_address": (228, 154),
    "person_involved_guardian": (328, 180),
    "date_of_incident": (228, 232),
    "time_of_incident": (478, 232),
    "facility_name": (278, 258),
    "incident_address": (278, 284),
    "was_employee_involved": (178, 309),
    "was_security_contacted": (398, 309),
    "was_law_contacted": (578, 309),
    "was_transported_ambulance": (428, 335),
    "ambulance_to_where": (278, 360),
    "type_of_incident": (272, 401),

    # Injury checkboxes (mark with "X")
    "injury_splinter": (87, 614),
    "injury_burn": (231, 614),
    "injury_heat_related": (339, 614),
    "injury_bruise": (87, 644),
    "injury_dental": (231, 644),
    "injury_head_neck_spinal": (339, 644),
    "injury_bite": (87, 673),
    "injury_stroke": (231, 673),
    "injury_choking": (339, 673),
    "injury_cut_scrape": (87, 702),
    "injury_heart_attack": (231, 702),
    "injury_other": (489, 702),

    "incident_summary": (100, 420),  # detailed account

    # Footer
    "employee_completing_report": (420, 170),
    "witness": (280, 130),
    "witness_phone": (630, 130),
}


def generate_pdf(incident: Incident) -> str:
    """Generate a incident report pdf and return its local filepath"""
    output_path = os.path.join(OUTPUT_DIR, f"incident_{incident.pk}.pdf")
    reader = PdfReader(TEMPLATE_PDF)
    writer = PdfWriter()

    writer.append(reader)
    writer.set_need_appearances_writer(True)

    data = _get_incident_dict(incident)
    writer.update_page_form_field_values(
        page=None,                 # None = all pages (per docs)
        fields=data,
        auto_regenerate=False,     # leave to viewers; we already set NeedAppearances
        flatten=False              # set True if you want to burn the text in (see below)
    )

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def _get_incident_dict(incident: Incident):
    data = incident.to_dict()
    data["date_of_report"] = data["created"].date()
    return data