"""
bodyfat_analyzer.py
-------------------
Body Fat Analyzer page for Coach E.
Accessible to both guests and logged-in users — no auth required.

Flow:
1. User selects unit system (Metric or Imperial)
2. User uploads a photo or uses camera
3. User optionally inputs body measurements
4. App runs Navy Formula on measurements (if provided)
5. App sends image + context to Groq Vision
6. Result is displayed — NOT saved to database (session only)

On page refresh: everything clears. Image is never persisted anywhere.
"""

import streamlit as st
from PIL import Image, ImageOps  # ImageOps.exif_transpose fixes iPhone upside-down photos

from bodyfat_utils import (
    image_to_base64,
    navy_formula,
    get_bf_category,
    analyze_bodyfat_with_groq,
    feet_inches_to_cm,
    inches_to_cm,
)


def render_bodyfat_analyzer():

    # ─────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────
    st.title("🔬 Body Fat Analyzer")
    st.markdown(
        "Upload a photo and let Coach E's AI estimate your body fat percentage. "
        "Add your measurements for a more accurate result."
    )

    st.info(
        "📌 **Note:** This is an AI-based estimate for general fitness awareness, not a medical measurement. "
        "For clinical accuracy, use DEXA scanning, MRI, or hydrostatic weighing. "
        "**Add ±3–5% margin of error to any result shown here.**",
        icon="ℹ️"
    )

    st.divider()

    # ─────────────────────────────────────────────
    # SESSION STATE INIT
    # Results live in session_state so they survive
    # widget interactions mid-page, but clear on
    # full refresh — by design (no DB).
    # ─────────────────────────────────────────────
    if "bf_result" not in st.session_state:
        st.session_state.bf_result = None
    if "navy_result" not in st.session_state:
        st.session_state.navy_result = None
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False

    # ─────────────────────────────────────────────
    # STEP 1 — BASIC INFO
    # Gender affects Navy formula thresholds.
    # Unit system affects all measurement inputs.
    # ─────────────────────────────────────────────
    st.subheader("Step 1 — Basic Info")

    col1, col2 = st.columns(2)

    with col1:
        gender = st.radio(
            "Biological sex",
            options=["Male", "Female"],
            horizontal=True,
            help="Used for Navy formula and ACE category thresholds."
        )

    with col2:
        # Toggle between metric and imperial
        # This controls all measurement input labels and conversions below
        unit_system = st.radio(
            "Unit system",
            options=["Metric (cm/kg)", "Imperial (ft, in)"],
            horizontal=True,
        )

    # Boolean flag — easier to check throughout the rest of the file
    is_imperial = unit_system == "Imperial (ft, in)"

    st.divider()

    # ─────────────────────────────────────────────
    # STEP 2 — PHOTO UPLOAD
    # file_uploader or camera_input both return
    # the same UploadedFile object type.
    # ─────────────────────────────────────────────
    st.subheader("Step 2 — Upload Your Photo")

    st.markdown(
        "For best results: **full body photo**, good lighting, minimal clothing. "
        "The AI analyzes muscle definition, fat distribution, and body shape."
    )

    photo_method = st.radio(
        "How would you like to provide your photo?",
        options=["📁 Upload a file", "📷 Use camera"],
        horizontal=True
    )

    uploaded_file = None

    if photo_method == "📁 Upload a file":
        uploaded_file = st.file_uploader(
            "Choose a photo",
            type=["jpg", "jpeg", "png"],
            help="Accepted formats: JPG, JPEG, PNG"
        )
    else:
        uploaded_file = st.camera_input("Take a photo")

    # Preview the uploaded photo
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Fix iPhone EXIF rotation — without this, iOS photos often render upside down
        image = ImageOps.exif_transpose(image)
        st.image(image, caption="Your uploaded photo", width=300)
        # Reset file pointer so image_to_base64() can read from byte 0 again
        uploaded_file.seek(0)

    st.divider()

    # ─────────────────────────────────────────────
    # STEP 3 — MEASUREMENTS (OPTIONAL)
    # All inputs start at 0.0 so the user just
    # types their number — no backspacing required.
    # Inputs adapt labels based on unit_system.
    # ─────────────────────────────────────────────
    st.subheader("Step 3 — Measurements (Optional but Recommended)")

    # Initialize all measurement variables to None
    # They only get real values if the expander is opened
    height_cm = None
    waist_cm  = None
    neck_cm   = None
    hip_cm    = None
    measurements_provided = False

    with st.expander("➕ Add body measurements for better accuracy", expanded=False):

        if is_imperial:
            st.markdown(
                "Using **Imperial units**. Height in feet + inches, "
                "circumferences in inches."
            )
        else:
            st.markdown(
                "Using **Metric units**. All measurements in centimeters."
            )

        # ── HEIGHT ──
        # Imperial splits into two fields: feet and inches
        # Metric is a single cm field
        if is_imperial:
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                height_ft = st.number_input(
                    "Height — feet",
                    min_value=0.0, max_value=8.0,
                    value=0.0, step=1.0,
                    format="%.0f"  # show as whole number
                )
            with h_col2:
                height_in = st.number_input(
                    "Height — inches",
                    min_value=0.0, max_value=11.0,
                    value=0.0, step=0.5
                )
            # Convert to cm for the formula
            height_cm = feet_inches_to_cm(height_ft, height_in)
        else:
            height_cm = st.number_input(
                "Height (cm)",
                min_value=0.0, max_value=250.0,
                value=0.0, step=0.5
            )

        # ── CIRCUMFERENCE MEASUREMENTS ──
        col1, col2 = st.columns(2)

        unit_label = "in" if is_imperial else "cm"

        with col1:
            waist_raw = st.number_input(
                f"Waist circumference ({unit_label})",
                min_value=0.0, max_value=200.0 if not is_imperial else 79.0,
                value=0.0, step=0.5,
                help="Measure at the navel level."
            )

        with col2:
            neck_raw = st.number_input(
                f"Neck circumference ({unit_label})",
                min_value=0.0, max_value=80.0 if not is_imperial else 31.0,
                value=0.0, step=0.5,
                help="Measure just below the larynx."
            )

        # Hip only needed for women
        hip_raw = None
        if gender == "Female":
            hip_raw = st.number_input(
                f"Hip circumference ({unit_label})",
                min_value=0.0, max_value=200.0 if not is_imperial else 79.0,
                value=0.0, step=0.5,
                help="Measure at the widest point."
            )

        # Convert imperial inches → cm if needed
        if is_imperial:
            waist_cm = inches_to_cm(waist_raw)
            neck_cm  = inches_to_cm(neck_raw)
            hip_cm   = inches_to_cm(hip_raw) if hip_raw is not None else None
        else:
            waist_cm = waist_raw
            neck_cm  = neck_raw
            hip_cm   = hip_raw

        # Mark that measurements were provided (expander was opened)
        measurements_provided = True

    st.divider()

    # ─────────────────────────────────────────────
    # STEP 4 — ANALYZE
    # Button is disabled until a photo is uploaded.
    # ─────────────────────────────────────────────
    st.subheader("Step 4 — Analyze")

    analyze_clicked = st.button(
        "🔍 Analyze My Body Fat",
        type="primary",
        disabled=(uploaded_file is None),
        use_container_width=True
    )

    if uploaded_file is None:
        st.caption("⬆️ Upload a photo above to enable analysis.")

    # ─────────────────────────────────────────────
    # ANALYSIS LOGIC
    # Runs Navy formula first (if measurements given),
    # then calls Groq Vision with image + context.
    # ─────────────────────────────────────────────
    if analyze_clicked and uploaded_file is not None:

        # Clear any previous results before re-running
        st.session_state.bf_result = None
        st.session_state.navy_result = None
        st.session_state.analyzed = False

        with st.spinner("Analyzing your photo... this takes a few seconds ⏳"):

            # Step A: Navy formula
            # Only runs if measurements were entered AND are non-zero
            # (value=0.0 default means user didn't fill it in)
            try:
                if (measurements_provided
                        and height_cm and height_cm > 100
                        and waist_cm and waist_cm > 40
                        and neck_cm and neck_cm > 20):
                    navy_estimate = navy_formula(
                        gender=gender,
                        height_cm=height_cm,
                        waist_cm=waist_cm,
                        neck_cm=neck_cm,
                        hip_cm=hip_cm if gender == "Female" else None
                    )
                else:
                    navy_estimate = None
            except Exception:
                navy_estimate = None

            st.session_state.navy_result = navy_estimate

            # Step B: Convert image to base64 for Groq
            filename = uploaded_file.name.lower() if hasattr(uploaded_file, "name") else "photo.jpg"
            mime_type = "image/png" if filename.endswith(".png") else "image/jpeg"

            uploaded_file.seek(0)
            image_b64 = image_to_base64(uploaded_file)

            # Step C: Groq Vision call
            try:
                result_text = analyze_bodyfat_with_groq(
                    image_b64=image_b64,
                    image_mime=mime_type,
                    gender=gender,
                    navy_estimate=navy_estimate
                )
                st.session_state.bf_result = result_text
                st.session_state.analyzed = True

            except Exception as e:
                st.error(f"Something went wrong with the AI analysis: {str(e)}")

    # ─────────────────────────────────────────────
    # RESULTS DISPLAY
    # ─────────────────────────────────────────────
    if st.session_state.analyzed and st.session_state.bf_result:

        st.divider()
        st.subheader("📊 Your Results")

        # Navy formula result (shown only if measurements were provided)
        if st.session_state.navy_result is not None:
            navy_val = st.session_state.navy_result
            category_info = get_bf_category(navy_val, gender)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="📐 Navy Formula Estimate",
                    value=f"{navy_val}%",
                    help="Calculated from your measurements using the U.S. Navy formula."
                )
            with col2:
                st.metric(
                    label="🏷️ Category",
                    value=category_info["label"],
                )

            st.caption(
                "The Navy formula is math-based and generally more reliable than visual estimation alone. "
                "The AI analysis below uses your photo and may differ slightly. "
                "Always add ±3–5% margin of error to either result."
            )
            st.divider()

        # Groq AI visual analysis
        st.markdown("### 🤖 AI Visual Analysis")
        st.markdown(st.session_state.bf_result)

        st.divider()

        # Remind user results aren't saved
        st.warning(
            "⚠️ **These results are not saved.** "
            "Refreshing the page will clear your photo and results. "
            "Take a screenshot if you want to keep them!",
            icon="💾"
        )

        if st.button("🔄 Start Over"):
            st.session_state.bf_result = None
            st.session_state.navy_result = None
            st.session_state.analyzed = False
            st.rerun()