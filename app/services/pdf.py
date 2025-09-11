import os
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

field_coords = {
    # Top section
    "person_involved": (278, 103),
    "age": (728, 103),
    "phone_number": (228, 129),
    "guest_of": (528, 129),
    "address": (228, 154),
    "parent_guardian": (328, 180),b
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

TEMPLATE_PDF = "./app/templates/Blank Incident Report (2)[35].pdf"
OUTPUT_DIR = "/tmp"

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

def _make_overlay(incident, overlay_path):
    """Create a transparent overlay PDF with text placed at coordinates."""
    c = canvas.Canvas(overlay_path, pagesize=letter)

    for field, coords in field_coords.items():
        if not coords:
            continue
        value = getattr(incident, field, None)
        if not value:
            continue

        x, y = coords

        # Handle yes/no fields as checkboxes
        if field.startswith("was_") or field.startswith("injury_"):
            if str(value).lower() in ["yes", "true", "1", "x", "checked"]:
                c.drawString(x, y, "X")
        else:
            # Draw normal text
            c.drawString(x, y, str(value))

    c.save()

def generate_pdf(incident):
    overlay_path = os.path.join(OUTPUT_DIR, f"incident_{incident.id}_overlay.pdf")
    output_path = os.path.join(OUTPUT_DIR, f"incident_{incident.id}.pdf")

    # Make overlay
    _make_overlay(incident, overlay_path)

    # Merge with background
    template_pdf = PdfReader(TEMPLATE_PDF)
    overlay_pdf = PdfReader(overlay_path)

    for page, overlay in zip(template_pdf.pages, overlay_pdf.pages):
        merger = PageMerge(page)
        merger.add(overlay).render()

    PdfWriter().write(output_path, template_pdf)
    return output_path
