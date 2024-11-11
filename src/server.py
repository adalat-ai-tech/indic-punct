from fastapi import FastAPI, HTTPException, Request, Response, Cookie, Query
from fastapi.responses import JSONResponse
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict
import traceback
import enum

from punctuate.punctuate_text import Punctuation
from inverse_text_normalization.run_predict import inverse_normalize_text

app = FastAPI()

LANGUAGES = ["en", "hi", "gu", "te", "mr", "kn", "pa", "ta", "bn", "or", "ml", "as"]

# Initialize display engines
ENGINE = {
    "itn": inverse_normalize_text,
    "punctuate": {
        lang_code: Punctuation(language_code=lang_code)
        for lang_code in LANGUAGES
    }
}


def get_app():
    return app, ENGINE


# Enum for error handling
class DisplayError(enum.Enum):
    lang_err = "Unsupported language ID requested. Please check available languages."
    string_err = "String passed is incompatible."
    internal_err = "Internal crash."
    unknown_err = "Unknown Failure."
    loading_err = "Loading failed. Check if metadata/paths are correctly configured."


## ---------------------------- API End-points ------------------------------ ##

@app.get('/languages')
async def supported_languages(display_user_id: Optional[str] = Cookie(None)):
    # Set user cookie if not present
    response = JSONResponse(content=LANGUAGES)
    if not display_user_id:
        response.set_cookie(key="display_user_id", value=uuid4().hex, max_age=365 * 24 * 60 * 60, samesite="None",
                            secure=True, httponly=True)
    return response


@app.get('/display/{lang_code}')
async def display_api(lang_code: str, text: str, punctuation: bool = Query(False, description="Apply punctuation if True")):
    # Check for errors and raise HTTP exception if needed
    if lang_code not in LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Invalid scheme identifier. Supported languages are: {LANGUAGES}")

    try:
        # Process ITN
        display_result = ENGINE["itn"]([text], lang=lang_code)[0]

        # Optionally apply punctuation
        if punctuation:
            display_result = ENGINE["punctuate"][lang_code].punctuate_text([display_result])[0]

    except Exception as e:
        print(traceback.format_exc())  # Log the error details for debugging
        display_result = DisplayError.internal_err

    # Check for errors and raise HTTP exception if needed
    if isinstance(display_result, DisplayError):
        raise HTTPException(status_code=500, detail=display_result.value)

    # Return the processed result
    return {
        "success": True,
        "input": text,
        "result": display_result,
        "at": f"{datetime.utcnow()} +0000 UTC"
    }
