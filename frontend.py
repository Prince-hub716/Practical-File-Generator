
import streamlit as st
import streamlit.components.v1 as components
from backend import workflow

st.set_page_config(page_title="Practical File Generator", page_icon="📘", layout="centered")
st.title("📘 Practical File Generator")

with st.form("input_form"):
    grade = st.text_input("Grade (e.g., BTech 1st year, 10th ...)")
    subject = st.text_input("Subject (e.g., Physics, Chemistry ...)")
    aim = st.text_input("Aim of the Practical")

    programming = st.checkbox("Does this involve programming?")

    # ✅ Section Selector
    st.subheader("📑 Choose sections to include in the file")
    section_options = [
        "Aim", "Apparatus", "Theory", "Procedure",
        "Observations", "Code", "Output", "Conclusion", "Diagrams"
    ]
    selected_sections = st.multiselect("Select subheadings", section_options, default=section_options)

    # ✅ New Feature 1: Add Observations
    st.subheader("📝 Add Your Observations (Optional)")
    custom_observations = st.text_area("Enter your observation readings (tables/points)", height=120)

    # ✅ New Feature 2: Upload Diagrams / Photos
    st.subheader("🖼️ Upload Diagrams or Output Photos")
    uploaded_images = st.file_uploader("Upload one or more images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    # ✅ New Feature 3: Add Code Output
    st.subheader("💻 Paste Code Output (Optional)")
    code_output = st.text_area("Paste the output of your code here", height=120)

    submit = st.form_submit_button("🚀 Generate Practical File")

if submit:
    st.info("⏳ Generating your practical file... please wait")

    # Prepare data for backend
    initial_data = {
        "grade": grade,
        "subject": subject,
        "aim": aim,
        "programming": programming,
        "observations": custom_observations if custom_observations else "",
        "diagram": uploaded_images if uploaded_images else None,
        "codes": "",
        "code_output": code_output if code_output else "",
        "selected_sections": selected_sections
    }

    final_data = workflow.invoke(initial_data)

    st.success("✅ Practical file generated!")

    # ✅ Style wrapper to fix dark mode issue
    styled_html = f"""
    <div style="background-color:white; color:black; padding:20px; border-radius:10px;">
        {final_data['file_combiner']}
    </div>
    """

    # ✅ Show file in preview
    st.subheader("📖 Practical File Preview")
    components.html(styled_html, height=600, scrolling=True)

    # ✅ Show uploaded images inside the preview
    if uploaded_images and "Diagrams" in selected_sections:
        st.subheader("📷 Uploaded Diagrams/Photos")
        for img in uploaded_images:
            st.image(img, caption=img.name)

    # ✅ Download button (save as HTML so Word can open it with styling)
    st.download_button(
        label="📥 Download Practical File (HTML)",
        data=final_data["file_combiner"],
        file_name="practical_file.html",
        mime="text/html"
    )


