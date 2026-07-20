"""
Curato Proposal Intelligence — Generic AI Client
Provider-agnostic client for structured data generation.
"""

import json
import time
from typing import Type, TypeVar, Optional, Any

from pydantic import BaseModel, ValidationError
import groq

from app.config import Settings

T = TypeVar("T", bound=BaseModel)

class AIClient:
    """Generic AI client that abstracts the underlying provider (Groq, etc.)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.ai_provider.lower()
        self.model = settings.ai_model
        
        if self.provider == "groq":
            self.client = groq.Groq(api_key=settings.groq_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def generate_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        max_retries: int = 3
    ) -> T:
        """
        Send a prompt to the AI provider and return a validated Pydantic model.
        Includes retry logic with exponential backoff for rate limits and parsing errors.
        """
        for attempt in range(max_retries):
            try:
                if self.provider == "groq":
                    content = self._call_groq(system_prompt, user_prompt)
                else:
                    raise ValueError(f"Unsupported AI provider: {self.provider}")
                
                print(f"Raw LLM response (attempt {attempt + 1}):\n{content}\n---")
                
                # Parse and validate the JSON response
                parsed = self._parse_and_validate(content, response_model)
                if parsed:
                    return parsed
                
                print(f"Generation attempt {attempt + 1}: failed to parse/validate response")
                
            except groq.RateLimitError:
                wait_time = (2 ** attempt) * 5
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except (groq.APIError, groq.APIConnectionError, groq.APITimeoutError) as e:
                print(f"API error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise
                    
            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise

            # Exponential backoff for parsing errors or non-rate-limit errors
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        raise ValueError("Failed to generate structured response after all retries.")

    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq API with JSON mode enabled."""
        # Ensure we ask for JSON explicitly in the prompt for Groq JSON mode
        if "json" not in system_prompt.lower() and "json" not in user_prompt.lower():
            system_prompt += "\n\nYou must output a valid JSON object."

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,  # Use 0 for more deterministic structured output
        )
        return response.choices[0].message.content

    def _parse_and_validate(self, content: str, response_model: Type[T]) -> Optional[T]:
        """Parse JSON and validate against the Pydantic model."""
        def parse_json_str(json_str: str) -> Optional[T]:
            try:
                data = json.loads(json_str)
                return response_model.model_validate(data)
            except ValidationError as e:
                print(f"Pydantic Validation Error:\n{e}")
                raise e # We raise so that the outer retry loop catches it and propagates the detailed error

        try:
            # Try direct JSON parse
            return parse_json_str(content)
        except json.JSONDecodeError as e:
            print(f"Direct JSON parse failed: {e}")
        except ValidationError:
            raise # Propagate validation error directly
            
        # Try extracting JSON from markdown code blocks if the model ignored response_format
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                return parse_json_str(json_str)
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
                return parse_json_str(json_str)
        except (json.JSONDecodeError, IndexError):
            pass
        except ValidationError:
            raise

        # Try finding JSON object in the text
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return parse_json_str(json_str)
        except json.JSONDecodeError:
            pass
        except ValidationError:
            raise

        return None
