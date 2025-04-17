# load SDK
from google import genai

# Set up the Google Gemini API client
import os
from google.auth.credentials import Credentials

GOOGLE_API_KEY = ""
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
# genai.configure(api_key=GOOGLE_API_KEY)


#Set up a retry helper. This allows you to "Run all" without worrying about per-minute quota.
from google.api_core import retry


is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

genai.models.Models.generate_content = retry.Retry(
    predicate=is_retriable)(genai.models.Models.generate_content)