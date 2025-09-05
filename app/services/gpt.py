from openai import AsyncOpenAI, RateLimitError, OpenAIError, Timeout, APIError
from app.config import settings
from fastapi import HTTPException
from app.schemas.schemas import IncidentSummary
import logging
import asyncio

client = AsyncOpenAI(api_key=settings.openai_api_key)

summary_extractor_prompt = """You are an assistant that extracts structured data from short incident reports.  
Fill in the following JSON schema.  

If information is not explicitly provided, infer reasonable defaults.  
- If medical attention was minor (e.g. band-aid), assume no security, law, or ambulance.
- If a body part is mentioned (e.g. "right arm cut"), extract it.
- If not mentioned, leave it as "" (empty string).  
- Use "yes" or "no" for boolean fields.  

Return ONLY valid JSON, no explanations."""

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

    except (RateLimitError, Timeout) as e:
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
  
async def generate_incident_followups(model: str, missing_fields: list[str]):
  pass