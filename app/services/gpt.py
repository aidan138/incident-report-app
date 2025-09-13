from openai import AsyncOpenAI, RateLimitError, OpenAIError, APIError, APITimeoutError
from app.config import settings
from fastapi import HTTPException
from app.schemas.incident_schemas import IncidentSummary
import logging
import asyncio
from pydantic import create_model, BaseModel


client = AsyncOpenAI(api_key=settings.openai_api_key)

summary_extractor_prompt = """You are an assistant that extracts structured data from short incident reports.  
Fill in the following JSON schema.  

If information is not explicitly provided, infer reasonable defaults.  
- If medical attention was minor (e.g. band-aid), assume no security, law, or ambulance.
- If a body part is mentioned (e.g. "right arm cut"), extract it.
- If not mentioned, leave it as "" (empty string).  
- Use "YES" or "NO" for boolean fields.
- For `location_of_incident`: extract where inside the facility the incident occurred (e.g. "staircase", "kids pool", "locker room"). If the location is not mentioned, leave it as "" (empty string).
- If `type_of_incident` = "Other", then `incident_other_exp` must contain the described type of incident. Otherwise, set `incident_other_exp` = "".
- If `type_of_injury` = "Other", then `injury_other_exp` must contain the described injury. Otherwise, set `injury_other_exp` = "".

Return ONLY valid JSON, no explanations."""

follow_up_prompt = """Generate follow-up questions for the first responder to a pool incident in JSON format to fill in missing fields for the report they provided using the following fields as keys:
{missing_fields}
Each value should be a polite, natural follow-up question asking for that field.
Do not add or remove fields. Use the keys exactly as provided.
Output key=field, value=follow-up."""

MAX_TRIES = 3
BACKOFF_FACTOR = 2


async def extract_incident_info(model: str, content: str) -> IncidentSummary:
  """Given a prompt, call a LLM to create a validated incident summary.

  Args:
      model (str): The name of the model to query.
      prompt (str): The incident summary that needs to be converted to JSON.
  Returns:
      IncidentSummary: Validated summary with missing info left as empty strings.
  Raises:
      HTTPException: When out of retries or API errors occur.
  """
  for attempt in range(1, MAX_TRIES + 1):
    try:
      response = await client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": summary_extractor_prompt},
            {
                "role": "user",
                "content": content,
            },
        ],
        text_format=IncidentSummary,
      )

      return response.output_parsed

    except (RateLimitError, APITimeoutError) as e:
      wait_time = attempt ** BACKOFF_FACTOR
      logging.warning(f"Attempt {attempt} failed from error: {e}. Retrying in {wait_time}s...")
      await asyncio.sleep(wait_time)
    except (APIError, OpenAIError, ValueError) as e:
      logging.error(f"OpenAI API error or invalid response: {e}")
      break
    except Exception as e:
      logging.critical(f"Unexpected error occurred {e}")
      break
  
  raise HTTPException(status_code=503, detail="Failed to extract incident summary from OpenAI API")
  
async def generate_incident_followups(model: str, missing_fields: list[str]) -> list[str]:

  for attempt in range(MAX_TRIES):
    try:
      FollowUps = _build_follow_ups_schema(missing_fields=missing_fields)
      response = await client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": "You are a helpful assistant that only can output valid JSON format."},
            {"role": "user", "content": follow_up_prompt.format(missing_fields=missing_fields)}
        ],
        text_format=FollowUps,
      )

      return response.output_parsed
    
    except (RateLimitError, APITimeoutError) as e:
      wait_time = attempt ** BACKOFF_FACTOR
      logging.warning(f"Attempt {attempt} failed from error: {e}. Retrying in {wait_time}s...")
      await asyncio.sleep(wait_time)
    except (APIError, OpenAIError, ValueError) as e:
      logging.error(f"OpenAI API error or invalid response: {e}")
      break
    except Exception as e:
      logging.critical(f"Unexpected error occurred {e}")
      break
    raise HTTPException(status_code=503, detail="Failed to create follow-up questions from OpenAI API")
      

def _build_follow_ups_schema(missing_fields: list[str]) -> BaseModel:
  """Generate unique Pydantic models on the fly for missing fields

  Args:
      missing_fields (list[str]): List of missing fields from an incident report.

  Returns:
      BaseModel: Output schema that requires each missing field has a string value
  """
  fields = {field: str for field in missing_fields}
  return create_model("FollowUps", **fields)
