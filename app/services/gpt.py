
Sample_prompt = """You are an assistant that extracts structured data from short incident reports.  
Fill in the following JSON schema.  

If information is not explicitly provided, infer reasonable defaults.  
- If medical attention was minor (e.g. band-aid), assume no security, law, or ambulance.  
- If a body part is mentioned (e.g. "right arm cut"), extract it.  
- If not mentioned, leave it as "" (empty string).  
- Use "yes" or "no" for boolean fields.  

Return ONLY valid JSON, no explanations.

Schema:
{
  "type_of_incident": "",
  "body_part_afflicted": "",
  "employee_involved": "yes/no",
  "security_contacted": "yes/no",
  "law_contacted": "yes/no",
  "transported_ambulance": "yes/no",
  "ambulance_to_where": "",
  "where_incident_occurred": "",
  "signs_symptoms": "",
  "type_of_injury": ""
}"""