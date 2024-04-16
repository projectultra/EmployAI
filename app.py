import replicate
import os
from flask import Flask, render_template, request

app = Flask(__name__)

os.environ["REPLICATE_API_TOKEN"] = "r8_Ofc4U8n0bodAQLZyxVtQ8f5S7KemqwL2BOPvn"  # Replace with your API token

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_name = request.form['user_name']
        company = request.form['company']
        manager = request.form['manager']
        role = request.form['role']
        referral = request.form['referral']
        prompt_input = request.form['prompt_input']
        temp = float(request.form['temp'])

        pre_prompt = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        prompt = f"The job description is: {prompt_input}\n"
        prompt += f"The candidate's name to include on the cover letter: {user_name}\n"
        prompt += f"The job title/role: {role}\n"
        prompt += f"The hiring manager is: {manager}\n"
        prompt += f"How I heard about the opportunity: {referral}\n."
        prompt += "Generate a cover letter"

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
        print(response)
        generated_cover_letter = " ".join([item for item in response])
        return generated_cover_letter

    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)