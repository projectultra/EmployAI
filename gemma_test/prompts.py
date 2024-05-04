from transformers import AutoModelForCausalLM, AutoTokenizer

# Load pre-trained tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it")

# Define your prompt
prompt = "Generate a personalized cover letter targeting the position of Data Analyst at Creative Capsule. Here are the key details to include: Education: Bachelors in Engineering. Experience: Fresher Achievements: Treasurer. Relevant Projects: Railway project. The cover letter should be addressed to Tom Mendes and highlight how my qualifications and experience make me a strong fit for this role. Please also mention LinkedIn as the referral for this opportunity.The cover letter should be well-structured, engaging, and no more than one page in length. It should convey my enthusiasm for the role and the company, while showcasing my relevant skills and accomplishments."

prompt_aa = "Generate an accomplishment-focused cover letter for the position of [Job Description] at [Company Name]. The cover letter should: 1. Highlight my most significant and relevant achievements from my experience and projects.2. Demonstrate how these achievements have prepared me for success in the target role.3. Convey my enthusiasm and fit for the company's culture and mission.Please include the following details:Education: [Education Details]Experience: [Work Experience DetailsAchievements: [Notable Achievements]Relevant Projects: [Relevant Project Details]The cover letter should be addressed to [Hiring Manager's Name] and mention [Referral Name] as the referral for this opportunity. It should be well-structured, engaging, and no more than one page in length."

prompt_a = "Generate a cover letter for the position of [Job Description] at [Company Name] by comparing and contrasting my background with the previous job posting details provided below:My Profile:Education: [Education Details]Experience: [Work Experience Details]Achievements: [Notable Achievements]Relevant Projects: [Relevant Project Details]Previous Job Posting:[Previous Job Description and Requirements]The cover letter should highlight how my qualifications and experiences align with or exceed the requirements outlined in the previous job posting. It should also address any potential gaps or areas where additional context may be needed.The cover letter should be tailored, well-written, and no more than one page in length. Please address it to [Hiring Manager's Name] and mention [Referral Name] as the referral for this opportunity."
# Tokenize the prompt
input_ids = tokenizer.encode(prompt_aa, return_tensors="pt")

# Generate response
outputs = model.generate(
    input_ids, max_length=2000, num_return_sequences=1, do_sample=True, temperature=0.98
)

# Decode and print response
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
