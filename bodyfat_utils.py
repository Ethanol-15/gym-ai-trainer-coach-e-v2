"""
bodyfat_utils.py
----------------
Utility functions for the Body Fat Analyzer feature in Coach E.

Contains:
- Unit conversion helpers (imperial → metric)
- Navy Body Fat Formula (math-based estimate from measurements)
- Groq Vision API call (AI-based estimate from photo)
- BF% category classifier
"""

import math
import base64
import os
from groq import Groq

# groq API key
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def get_groq_client():
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY.")
    return Groq(api_key=GROQ_API_KEY)


# UNIT CONVERSION HELPERS
# All conversions go → centimeters, since the
# Navy formula always works in metric internally.

def feet_inches_to_cm(feet: float, inches: float) -> float:
    """Converts height in feet + inches to centimeters."""
    total_inches = (feet * 12) + inches
    return total_inches * 2.54

def inches_to_cm(inches: float) -> float:
    """Converts a circumference measurement from inches to centimeters."""
    return inches * 2.54


# NAVY BODY FAT FORMULA
# Always receives centimeters — conversion is
# handled before calling this function.
# Returns a float percentage, e.g. 18.4

def navy_formula(gender: str, height_cm: float, waist_cm: float,
                 neck_cm: float, hip_cm: float = None) -> float | None:
    """
    U.S. Navy Body Fat Formula.
    All inputs must be in centimeters.
    Returns estimated BF% as a float, or None if inputs are invalid.
    """
    try:
        if gender == "Male":
            # Formula requires waist > neck to avoid log of zero/negative
            if waist_cm <= neck_cm:
                return None
            bf = (495 / (
                1.0324
                - 0.19077 * math.log10(waist_cm - neck_cm)
                + 0.15456 * math.log10(height_cm)
            )) - 450

        else:  # Female
            # Female formula also needs hip measurement
            if hip_cm is None or waist_cm + hip_cm <= neck_cm:
                return None
            bf = (495 / (
                1.29579
                - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm)
                + 0.22100 * math.log10(height_cm)
            )) - 450

        # Clamp to a sane range (formula can go haywire on bad inputs)
        return round(max(3.0, min(60.0, bf)), 1)

    except (ValueError, ZeroDivisionError):
        return None


# BF% CATEGORY CLASSIFIER
# Based on ACE (American Council on Exercise) ranges.
# Returns label + color hint for the UI.
def get_bf_category(bf_percent: float, gender: str) -> dict:
    """Returns a dict with 'label' and 'color' based on BF% and gender."""
    if gender == "Male":
        if bf_percent < 6:
            return {"label": "Essential Fat", "color": "blue"}
        elif bf_percent < 14:
            return {"label": "Athlete", "color": "green"}
        elif bf_percent < 18:
            return {"label": "Fitness", "color": "lime"}
        elif bf_percent < 25:
            return {"label": "Average", "color": "orange"}
        else:
            return {"label": "Obese", "color": "red"}
    else:
        if bf_percent < 14:
            return {"label": "Essential Fat", "color": "blue"}
        elif bf_percent < 21:
            return {"label": "Athlete", "color": "green"}
        elif bf_percent < 25:
            return {"label": "Fitness", "color": "lime"}
        elif bf_percent < 32:
            return {"label": "Average", "color": "orange"}
        else:
            return {"label": "Obese", "color": "red"}


# ─────────────────────────────────────────────
# IMAGE → BASE64
# Converts uploaded Streamlit file to base64
# so it can be sent in the Groq API payload.
# The image is NOT stored anywhere — memory only.
# ─────────────────────────────────────────────
def image_to_base64(uploaded_file) -> str:
    """
    Takes a Streamlit UploadedFile object and returns
    a base64-encoded string of the image bytes.
    """
    image_bytes = uploaded_file.read()
    return base64.b64encode(image_bytes).decode("utf-8")


# GROQ VISION CALL
# Sends the image (+ optional measurements) to
# Llama 4 Scout on Groq and returns the AI's
# body fat analysis as a plain text string.
def analyze_bodyfat_with_groq(
    image_b64: str,
    image_mime: str,
    gender: str,
    navy_estimate: float | None = None
) -> str:
    """
    Calls Groq's vision model with the user's image.

    Parameters:
    - image_b64     : base64-encoded image string
    - image_mime    : MIME type e.g. "image/jpeg" or "image/png"
    - gender        : "Male" or "Female"
    - navy_estimate : optional float from navy_formula(), used as anchor

    Returns:
        The model's response as a string.
    """

    client = get_groq_client()

    # Build the measurement context if available
    if navy_estimate is not None:
        measurement_context = (
            f"Additionally, based on the user's body measurements, "
            f"the U.S. Navy Body Fat Formula estimates their body fat at "
            f"{navy_estimate}%. Use this as a cross-reference anchor — "
            f"your visual estimate should be in a similar range unless you "
            f"have strong visual evidence to differ."
        )
    else:
        measurement_context = (
            "No body measurements were provided. "
            "Base your estimate purely on visual cues, but apply all bias "
            "corrections listed in your instructions."
        )

    # System prompt with bias correction rules (Option 2 + Option 4)
    system_prompt = """You are a professional fitness and body composition analyst.
Your job is to estimate a person's body fat percentage from a photo using visual cues
such as muscle definition, vascularity, fat distribution around the abdomen, face, and limbs.

CRITICAL ESTIMATION RULES — read these before forming any estimate:
- Strong lighting, shadows, and contrast create an illusion of lower body fat by
  enhancing muscle definition. Always adjust your estimate UPWARD by 2-4% to
  compensate for this effect.
- Overhead or downward angles exaggerate leanness and abdominal definition.
  If the photo appears to be taken from above, adjust UPWARD by an additional 1-3%.
- Flexed or tensed muscles appear more defined than at rest. Account for this.
- Skin tone, tan, and body hair can affect the appearance of definition.
- A single photo cannot capture the full picture — always give a WIDE range of
  at least 4-6 percentage points to reflect this uncertainty honestly.
- When in doubt, estimate HIGHER not lower. It is better to be conservative
  than to underestimate body fat due to flattering photo conditions.

Always:
- Give a body fat RANGE spanning at least 4-6% (e.g. "13–18%"), never a narrow range
- Explain which visual cues AND which bias corrections influenced your estimate
- State the ACE body fat category (Essential Fat / Athlete / Fitness / Average / Obese)
- Include a clear disclaimer about the ±3-5% margin of error inherent to photo-based estimation
- Be respectful and clinical in tone — no judgmental language

Format your response clearly with these sections:
1. Estimated Body Fat Range
2. Category
3. Visual Observations & Bias Corrections Applied
4. Accuracy Disclaimer"""

    # Build the user message — image + text combined
    user_message = {
        "role": "user",
        "content": [
            {
                # The actual image sent as base64
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_mime};base64,{image_b64}"
                }
            },
            {
                "type": "text",
                "text": (
                    f"Please analyze this {gender.lower()}'s body composition "
                    f"and estimate their body fat percentage. {measurement_context}"
                )
            }
        ]
    }

    # API call — Llama 4 Scout is Groq's current vision model
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            user_message
        ],
        max_tokens=600,
        temperature=0.3,  # low = consistent, less hallucination-prone
    )

    return response.choices[0].message.content