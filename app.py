import replicate
import os
from flask import Flask, render_template, request, session
from flask_pymongo import PyMongo
app = Flask(__name__)
app.secret_key="hehe"
app.config['MONGO_URI'] = 'mongodb+srv://newuser:test123@cluster0.jigcmlg.mongodb.net/user_details?retryWrites=true&w=majority'
os.environ["REPLICATE_API_TOKEN"] = "r8_Ofc4U8n0bodAQLZyxVtQ8f5S7KemqwL2BOPvn"  # Replace with your API token
app.config['MONGO_DBNAME']='user_details'
client = PyMongo(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    test=client.db.user
    test.insert_one({'h':'k'}).inserted_id
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

@app.route('/addlink')
def addlink():
    return '''<div id="dummylink"></div><br>
<div class="new-line">
    <div class="col-md col-sm-12 form-group mb-3" data-for="name">
        <input type="text" name="name" placeholder="Link Type(linkedin..)" data-form-field="name" class="form-control" value="" id="name-form1-t">
    </div>
</div>
<div class="new-line">
    <div class="col-md col-sm-12 form-group mb-3" data-for="email">
        <input type="email" name="email" placeholder="Link" data-form-field="email" class="form-control" value="" id="email-form1-t">
    </div>
</div>'''

@app.route('/addeducation')
def addeducation():
    return '''<br><div id="dummyeducation"></div><div class="col-md col-sm-12 form-group mb-3" data-for="name">
                                <input type="text" name="name" placeholder="Standard/Degree" data-form-field="name"
                                    class="form-control" value="" id="name-form1-t">
                            </div>
                            <div class="col-md col-sm-12 form-group mb-3" data-for="email">
                                <input type="email" name="email" placeholder="Percentage/CGPA" data-form-field="email"
                                    class="form-control" value="" id="email-form1-t">
                            </div>
                            <div class="col-md col-sm-12 form-group mb-3" data-for="email">
                                <input type="email" name="email" placeholder="year of completion" data-form-field="email"
                                    class="form-control" value="" id="email-form1-t">
                            </div>
                            <div class="col-12 form-group mb-3" data-for="textarea">
                                <input type="email" name="email" placeholder="College/School Name" data-form-field="email"
                                class="form-control" value="" id="email-form1-t">
                            </div>'''
                            
@app.route('/addexperience')
def addexperience():
    return '''<div class="col-md col-sm-12 form-group mb-3" data-for="name">
                                <input type="text" name="name" placeholder="Designation" data-form-field="name"
                                    class="form-control" value="" id="name-form1-t">
                            </div>
                            <div class="col-md col-sm-12 form-group mb-3" data-for="email">
                                <input type="email" name="email" placeholder="Start-date" data-form-field="email"
                                    class="form-control" value="" id="email-form1-t">
                                    
                            </div>
                            <div class="col-md col-sm-12 form-group mb-3" data-for="email">
                                <input type="email" name="email" placeholder="End-date" data-form-field="email"
                                    class="form-control" value="" id="email-form1-t">
                                    
                            </div>
                            <div class="col-12 form-group mb-3" data-for="textarea">
                                <input type="text" name="name" placeholder="Organization Name" data-form-field="name"
                                    class="form-control" value="" id="name-form1-t">
                            </div>
                            <div class="col-12 form-group mb-3" data-for="textarea">
                                <textarea name="textarea" placeholder="Work Experience" data-form-field="textarea"
                                    class="form-control form-textarea" id="textarea-form1-t"></textarea>
                            </div>
                            <div id="dummyexperience"></div>'''
@app.route('/details', methods=['POST'])
def details():
    list=request.form
    for key in request.form:
        print(key," : ",request.form[key])
    dict = {}
    dict['name'] = request.args.get('name')
    data=client.db.user
    data.insert_one(request.form.to_dict())
    
    return dict
@app.route('/dashboard')
def dashboard():
    session['education']=0
    session['experience']=0
    return render_template("DetailsForm.html")

@app.route('/login')

def authentication():
    return render_template("login.html")
if __name__ == '__main__':
    app.run(debug=True)