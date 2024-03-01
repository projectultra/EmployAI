import replicate
import os
os.environ["REPLICATE_API_TOKEN"] = "r8_X7Upw1buuHLhytCEICNSvKnIOSpxmIY3Bg3bY"  # put your api_token

import streamlit as st
# Load model directly
#from transformers import AutoTokenizer, AutoModelForCausalLM
#
#tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
#model = AutoModelForCausalLM.from_pretrained("google/gemma-2b")

st.markdown("""
<style>
.stApp {
  background-color: black;
}
</style>
""", unsafe_allow_html=True
)

# Define the Streamlit app layout
st.title("Cover Letter Generator with Llama 2")

with st.form('form to generate cover letter'):
    # User input for cover letter
    st.markdown("### Cover Letter Details")
    user_name = st.text_input("Name")
    company = st.text_input("Company Name")
    manager = st.text_input("Hiring Manager")
    role = st.text_input("Job Title")
    referral = st.text_input("How did you find out about this opportunity?")
    prompt_input = st.text_area("Paste the job description")
    temp = st.number_input('AI Temperature. Reflects the model creativity on a scale of 0 to 1', value=0.5)

    # Generate LLM response
    generate_cover_letter = st.form_submit_button("Generate Cover Letter")



if generate_cover_letter:
    # Prompts
    pre_prompt = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    # Create a prompt for LLM: Include user inputs, and job description in the prompt
    prompt = f"The job description is: {prompt_input}\n"
    prompt += f"The candidate's name to include on the cover letter: {user_name}\n"
    prompt += f"The job title/role: {role}\n"
    prompt += f"The hiring manager is: {manager}\n"
    prompt += f"How I heard about the opportunity: {referral}\n."
    prompt += "Generate a cover letter"
    # Generate LLM response
    with st.spinner("Generating response"):
        response = replicate.run(
    "google-deepmind/gemma-2b:26b2c530f16236a4816611509730c2e6f7b27875a6d33ec5cff42961750c98d8",
    input={
        "top_k": 50,
        "top_p": 0.95,
        "prompt": f"{pre_prompt} {prompt} Assistant:",
        "temperature": temp,
        "max_new_tokens": 512,
        "min_new_tokens": -1,
        "repetition_penalty": 1
    }
)
#        "prompt": f"{pre_prompt} {prompt} Assistant:",
#        "temperature": temp,
        # Extract and display the LLM-generated cover letter
        generated_cover_letter = " ".join([item for item in response])

    st.subheader("Generated Cover Letter:")
    st.write(generated_cover_letter)
    # Offer a download link for the generated cover letter
    st.subheader("Download Generated Cover Letter:")
    st.download_button("Download Cover Letter as TXT", generated_cover_letter, key="cover_letter")
