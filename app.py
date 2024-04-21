import replicate
import os
from bson.objectid import ObjectId
from flask import Flask, render_template, request, session, url_for,redirect
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
from flask_session import Session
app = Flask(__name__)
app.secret_key="hehe"
app.config['MONGO_URI'] = 'mongodb+srv://newuser:test123@cluster0.jigcmlg.mongodb.net/user_details?retryWrites=true&w=majority'
os.environ["REPLICATE_API_TOKEN"] = "r8_Ofc4U8n0bodAQLZyxVtQ8f5S7KemqwL2BOPvn"  # Replace with your API token
app.config['MONGO_DBNAME']='user_details'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
client = PyMongo(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('loggin'))
    test=client.db.user
   
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



@app.route('/addlink')
def addlink():
    session['link']=session['link']+1
    return f'''</div><br>
<div class="new-line">
    <div class="col-md col-sm-12 form-group mb-3" data-for="name">
        <input type="text" name="linkName{session['link']}" placeholder="Link Name(linkedin..)" data-form-field="name" class="form-control" value="" id="name-form1-t">
    </div>
</div>
<div class="new-line">
    <div class="col-md col-sm-12 form-group mb-3" data-for="email">
        <input type="test" name="link{session['link']}" placeholder="Link" data-form-field="email" class="form-control" value="" id="email-form1-t">
    </div>
</div><div id="dummylink">'''

@app.route('/addeducation')
def addeducation():
    session['education']=session['education']+1
    return f'''<br><div class="col-md col-sm-12 form-group mb-3" data-for="DegreeName1">
                                    <input type="text" name="degreeName{session['education']}" placeholder="Standard/Degree" data-form-field="name"
                                        class="form-control" value="" id="DegreeName1">
                                </div>
                                <div class="col-md col-sm-12 form-group mb-3" data-for="percentage{session['education']}">
                                    <input type="text" name="percentage{session['education']}" placeholder="Percentage/CGPA"
                                         class="form-control" value="" id="percentage{session['education']}">
                                </div>
                                <div class="col-md col-sm-12 form-group mb-3" data-for="year_of_completion{session['education']}">
                                    <input type="text" name="year_of_completion{session['education']}" placeholder="year of completion{session['education']}"
                                        data-form-field="year_of_completion{session['education']}" class="form-control" value="" id="year_of_completion{session['education']}">
                                </div>
                                <div class="col-12 form-group mb-3" data-for="collegeName{session['education']}"">
                                    <input type="   text" name="collegeName{session['education']}" placeholder="College/School Name"
                                        data-form-field="collegeName{session['education']}"" class="form-control" value="" id="collegeName{session['education']}"">
                                </div>
                                <div id="dummyeducation"></div>'''
                            
@app.route('/addexperience')
def addexperience():
    session['experience']=session['experience']+1
    return f'''<div class="col-md col-sm-12 form-group mb-3" data-for="name">
                                <input type="text" name="workName{session['experience']}" placeholder="Designation" data-form-field="name"
                                    class="form-control" value="" id="workName{session['experience']}">
                            </div>
                            <div class="col-md col-sm-12 form-group mb-3" data-for="start-date{session['experience']}">
                                <input type="text" name="start-date{session['experience']}" placeholder="Start-date" 
                                    class="form-control" value="" id="start-date{session['experience']}">
                                    
                            </div>
                            <div class="col-md col-sm-12 form-group mb-3" data-for="email">
                                <input type="text" name="end-date{session['experience']}" placeholder="End-date" data-form-field="end-date{session['experience']}"
                                    class="form-control" value="" id="end-date{session['experience']}">
                                    
                            </div>
                            <div class="col-12 form-group mb-3" data-for="orgName{session['experience']}">
                                <input type="text" name="orgName{session['experience']}" placeholder="Organization Name" 
                                    class="form-control" value="" id="orgName{session['experience']}">
                            </div>
                            <div class="col-12 form-group mb-3" data-for="details{session['experience']}">
                                <textarea name="details{session['experience']}" placeholder="Work experience" data-form-field="textarea"
                                    class="form-control form-textarea" id="details{session['experience']}"></textarea>
                            </div>
                            <div id="dummyexperience"></div>'''
@app.route('/details', methods=['POST'])
def details():
    form_data=request.form
    for key in request.form:
        print(key," : ",request.form[key])
    dict = {}
    dict['name'] = request.args.get('name')
    data=client.db.user
    details = {
    'personal_details': {
        'name': form_data['name'],
        'address': form_data['textarea'],
        'email': form_data['email'],
        'link': {}
    },
    'education': {},
    'experience': {}
    }

    # Iterate over form_data keys to find link, education, and experience entries dynamically
    for key in form_data.keys():
        if key.startswith('link'):
            link_num = key.replace('link', '')  # Extract the link number
            details['personal_details']['link'][f'link{link_num}'] = form_data[key]
        elif key.startswith('degreeName'):
            education_num = key.replace('degreeName', '')  # Extract the education number
            details['education'][f'education{education_num}'] = {
                'degreeName': form_data[f'degreeName{education_num}'],
                'percentage': form_data[f'percentage{education_num}'],
                'year_of_completion': form_data[f'year_of_completion{education_num}'],
                'collegeName': form_data[f'collegeName{education_num}']
            }
        elif key.startswith('workName'):
            experience_num = key.replace('workName', '')  # Extract the experience number
            details['experience'][f'experience{experience_num}'] = {
                'workName': form_data[f'workName{experience_num}'],
                'start-date': form_data[f'start-date{experience_num}'],
                'end-date': form_data[f'end-date{experience_num}'],
                'orgName': form_data[f'orgName{experience_num}'],
                'details': form_data[f'details{experience_num}']
            }
    user_id = ObjectId(session['user_id'])
    result = data.update_one(
    {'_id': user_id},
    {'$set': {'details': details}})
    return dict


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('loggin'))
    session['education']=1
    session['experience']=1
    session['link']=0
    return render_template("DetailsForm.html")


@app.route('/login', methods=['GET', 'POST'])
def loggin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = client.db.user.find_one({'email': email})
        if(user):
            if user and check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                # Increment failed login attempt count and lock out account if necessary
                client.db.user.update_one({'email': email}, {'$inc': {'failed_attempts': 1}})
                user = client.db.user.find_one({'email': email})
                if user['failed_attempts'] >= 5:
                    client.db.user.update_one({'email': email}, {'$set': {'is_locked': True}})
                    return render_template('login.html', error='Your account has been locked due to too many failed login attempts. Please reset your password.')
                return render_template('login.html', error='Invalid email or password.')
    return render_template('login.html')

@app.route('/signin',methods=['GET','POST'])
def siggnin():
    if request.method == 'POST':
        email = request.form['email']
        name =request.form['name']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        if client.db.user.find_one({'email': email}):
            return render_template('login.html', error='Email already registered.')
        session['logged_in'] = True
        client.db.user.insert_one({'email': email, 'password': hashed_password,'name':name})
        user=client.db.user.find_one({'email':email})
        session['user_id'] = str(user['_id'])
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/interview')
def interview():
    return render_template('interview.html')

@app.route('/interview_submit')
def interview_submit():
    if request.method=='POST':
        job_description = request.form['job_description']
        role= request.form['role']


@app.route('/cv-generator')
def cv_generator():
    if(request.method=='POST'):
        pass
    return render_template('cv_generator.html')

if __name__ == '__main__':
    app.run(debug=True)