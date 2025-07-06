from flask import Flask, request, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
import pdfplumber
import re
from flask_cors import CORS
import pymongo
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from textblob import TextBlob
import nltk
from collections import Counter
import string

# Download required NLTK data (do this once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Initialize stopwords
stop_words = set(stopwords.words('english'))

try:
    client = pymongo.MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("✅ MongoDB connected successfully.")
    db = client['smartjob_db']
    collection = db['skills']
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    client = None

@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    new_user = {
        "username": username,
        "email": email,
        "password": password,
        "skills": [],
        "history": [],
    }
    collection.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        email = data.get("email")
        new_skills = data.get("skills", [])

        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not new_skills:
            return jsonify({"error": "No skills provided"}), 400

        user = collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        existing_skills = user.get("skills", [])
        combined_skills = list(set(existing_skills + new_skills))
        collection.update_one({"email": email}, {"$set": {"skills": combined_skills}})

        return jsonify({"status": "success", "updated_skills": combined_skills})

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

skill_tagss = [
    "machine learning", "ML", "deep learning", "NLP", "natural language processing",
    "computer vision", "CV", "data analysis", "data analytics", "EDA",
    "web development", "full stack development", "software engineering",
    "cloud computing", "AWS", "Azure", "React", "React.js", "Node", "Node.js",
    "Big Data", "Bigdata", "generative ai", "TensorFlow", "PyTorch", "SQL", "MongoDB"
]

def clean_text(text):
    """Clean and normalize text for better matching"""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text)       # Remove extra spaces
    return text.strip()

def calculate_text_similarity(text1, text2):
    """Calculate simple similarity between two texts using word overlap"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0

def extract_skills_from_text(text, skill_tags, threshold=0.3):
    """
    Extract skills from text using lightweight pattern matching and context analysis
    Replaces the heavy sentence-transformers approach
    """
    text_clean = clean_text(text)
    detected_skills = set()
    
    # Enhanced skill variations for better matching
    skill_variations = {}
    for skill in skill_tags:
        variations = [skill.lower()]
        # Add common variations
        if skill.lower() == "machine learning":
            variations.extend(["ml", "machine-learning", "machinelearning"])
        elif skill.lower() == "deep learning":
            variations.extend(["deeplearning", "deep-learning", "neural networks"])
        elif skill.lower() == "natural language processing":
            variations.extend(["nlp", "text processing", "text analytics"])
        elif skill.lower() == "react.js":
            variations.extend(["react", "reactjs"])
        elif skill.lower() == "node.js":
            variations.extend(["node", "nodejs"])
        
        skill_variations[skill] = variations
    
    # Method 1: Direct keyword matching with word boundaries
    for skill in skill_tags:
        for variation in skill_variations.get(skill, [skill.lower()]):
            pattern = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern, text_clean):
                detected_skills.add(skill)
                break
    
    # Method 2: Context-based matching for skills not found directly
    sentences = sent_tokenize(text)
    for sentence in sentences:
        sentence_clean = clean_text(sentence)
        if len(sentence_clean.split()) > 3:  # Only process meaningful sentences
            
            for skill in skill_tags:
                if skill in detected_skills:
                    continue  # Skip if already found
                
                # Calculate similarity with the skill
                skill_clean = clean_text(skill)
                similarity = calculate_text_similarity(sentence_clean, skill_clean)
                
                if similarity > threshold:
                    # Additional context check
                    skill_words = skill_clean.split()
                    sentence_words = sentence_clean.split()
                    
                    # Check if most skill words appear in the sentence
                    matches = sum(1 for word in skill_words if word in sentence_words)
                    if matches >= len(skill_words) * 0.7:  # 70% of skill words must match
                        detected_skills.add(skill)
    
    # Method 3: Fuzzy matching for common abbreviations and variations
    common_patterns = {
        r'\bml\b': ['machine learning', 'ML'],
        r'\bnlp\b': ['natural language processing', 'NLP'],
        r'\bcv\b': ['computer vision', 'CV'],
        r'\baws\b': ['AWS'],
        r'\bsql\b': ['SQL'],
        r'\breact\b': ['React', 'React.js'],
        r'\bnode\b': ['Node', 'Node.js'],
        r'\bai\b': ['generative ai'],
    }
    
    for pattern, skills in common_patterns.items():
        if re.search(pattern, text_clean):
            for skill in skills:
                if skill in skill_tags:
                    detected_skills.add(skill)
    
    return list(detected_skills)

@app.route("/upload-resume", methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['resume']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported."}), 400

    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    detected_skills = extract_skills_from_text(text, skill_tagss)
    gmail_matches = re.findall(r'[\w\.-]+@gmail\.com', text)
    email_found = gmail_matches[0] if gmail_matches else None

    if email_found:
        user_doc = collection.find_one({"email": email_found})
        if user_doc:
            existing_skills = user_doc.get("skills", [])
            merged_skills = list(set(existing_skills + detected_skills))
            collection.update_one({"email": email_found}, {"$set": {"skills": merged_skills}})

    return jsonify({"filename": file.filename, "detected_skills": detected_skills, "extracted_email": email_found})

def fetch_jobs():
    URL = "https://aijobs.net/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    job_links = soup.find_all('a', class_='col py-2', href=True)
    jobs = []

    for job_link in job_links:
        link = "https://aijobs.net" + job_link.get('href')
        location = job_link.find('span', class_='d-none d-md-block text-break mb-1') or job_link.find('span', class_='d-block d-md-none text-break mb-1')
        location = location.get_text(strip=True) if location else "Not specified"

        employment_type = job_link.find('span', class_='badge rounded-pill text-bg-secondary my-md-1 ms-1')
        employment_type = employment_type.get_text(strip=True) if employment_type else "Not specified"

        experience_level = job_link.find('span', class_='badge rounded-pill text-bg-info my-md-1 d-none d-md-inline-block') or job_link.find('span', class_='badge rounded-pill text-bg-info my-md-1 d-md-none')
        experience_level = experience_level.get_text(strip=True) if experience_level else "Not specified"

        salary_div = job_link.find('div', class_='d-block mb-4')
        salary = salary_div.find('span', class_='badge rounded-pill text-bg-success d-none d-md-inline-block') or salary_div.find('span', class_='badge rounded-pill text-bg-success d-md-none') if salary_div else None
        salary = salary.get_text(strip=True) if salary else "Not specified"

        company_span = job_link.find('span', class_='text-muted')
        company = company_span.get_text(strip=True).split('Remote-first')[0].replace('\xa0', ' ').strip() if company_span else "Not specified"

        h5_element = job_link.find('h5', class_='fw-normal text-body-emphasis text-break')
        title = h5_element.get_text(strip=True).split('Featured')[0].replace('\xa0', ' ').strip() if h5_element else "Not specified"

        skill_tags = [span.get_text(strip=True) for span in job_link.find_all('span', class_='badge rounded-pill text-bg-light') if not span.get_text(strip=True).startswith('+')]
        benefit_tags = [sibling.get_text(strip=True) for sibling in job_link.find_all('span', class_='badge text-bg-success') if not sibling.get_text(strip=True).startswith('+')]

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'employment_type': employment_type,
            'experience_level': experience_level,
            'salary': salary,
            'skill_tags': ', '.join(skill_tags) if skill_tags else 'No skills listed',
            'benefit_tags': ', '.join(benefit_tags) if benefit_tags else 'No benefits listed',
            'link': link
        })
    return jobs

def create_email_content(job_list):
    if not job_list:
        return "No new AI/ML/NLP job opportunities found today."

    message = "*Your Daily AI/ML/NLP Job Alerts*\n\n"
    for job in job_list:
        message += f"🔹 **{job['title']}** at *{job['company']}* ({job['location']})\n"
        message += f"   • Employment Type: {job['employment_type']}\n"
        message += f"   • Experience Level: {job['experience_level']}\n"
        message += f"   • Salary: {job['salary']}\n"
        message += f"   • Required Skills: {job['skill_tags']}\n"
        message += f"   • Benefits: {job['benefit_tags']}\n"
        message += f"   • Apply here 👉 {job['link']}\n"
        message += f"{'-'*60}\n\n"
    return message + "🚀 Stay tuned — new opportunities coming your way soon!"

def mains():
    jobs = fetch_jobs()
    users = list(collection.find({}, {'_id': 0}))
    EMAIL_USER = 'pramodhdusa3720@gmail.com'
    EMAIL_PASS = 'xjky ntcz jmzq hizl'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)

    for user in users:
        email = user['email']
        user_skills = [skill.lower() for skill in user.get('skills', [])]
        history = user.get('history', [])

        for job in jobs:
            combined_text = f"{job['title']} {job['skill_tags']}".lower().replace(' ', '')
            if any(skill in combined_text for skill in user_skills) and job['title'] not in history:
                msg = EmailMessage()
                msg['Subject'] = "🔥 Your Personalized AI Job Alert"
                msg['From'] = EMAIL_USER
                msg['To'] = email
                msg.set_content(create_email_content([job]))
                server.send_message(msg)
                collection.update_one({"email": email}, {"$addToSet": {"history": job['title']}})
                break
    server.quit()
    print("✅ Job alert emails sent.")

scheduler = BackgroundScheduler()
scheduler.add_job(mains, 'cron', hour=16, minute=55)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)












from flask import Flask, request, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from sentence_transformers import SentenceTransformer, util
import pdfplumber
import re
from flask_cors import CORS
import pymongo
from datetime import datetime
import os
import spacy
import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()
import os
MONGO_URI = os.getenv("MONGO_URI")


app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
model = SentenceTransformer('all-MiniLM-L6-v2')


try:
    client = pymongo.MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("✅ MongoDB connected successfully.")
    db = client['smartjob_db']
    collection = db['skills']
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    client = None

@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    new_user = {
        "username": username,
        "email": email,
        "password": password,
        "skills": [],
        "history": [],
    }
    collection.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        email = data.get("email")
        new_skills = data.get("skills", [])

        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not new_skills:
            return jsonify({"error": "No skills provided"}), 400

        user = collection.find_one({"email": email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        existing_skills = user.get("skills", [])
        combined_skills = list(set(existing_skills + new_skills))
        collection.update_one({"email": email}, {"$set": {"skills": combined_skills}})

        return jsonify({"status": "success", "updated_skills": combined_skills})

    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

skill_tagss = [
    "machine learning", "ML", "deep learning", "NLP", "natural language processing",
    "computer vision", "CV", "data analysis", "data analytics", "EDA",
    "web development", "full stack development", "software engineering",
    "cloud computing", "AWS", "Azure", "React", "React.js", "Node", "Node.js",
    "Big Data", "Bigdata", "generative ai", "TensorFlow", "PyTorch", "SQL", "MongoDB"
]

def extract_skills_from_text(text, skill_tags, threshold=0.65):
    text = re.sub(r'\s+', ' ', text).lower()
    sentences = [s.strip() for s in re.split(r'[.,;\n\u2022\-\u2013()]', text) if len(s.strip()) > 10]
    skill_embeddings = model.encode([s.lower() for s in skill_tags])
    detected_skills = set()

    for skill in skill_tags:
        if re.search(r'\\b' + re.escape(skill.lower()) + r'\\b', text.lower()):
            detected_skills.add(skill)

    for sentence in sentences:
        if len(sentence.split()) > 3:
            sentence_embedding = model.encode(sentence)
            similarities = util.cos_sim(sentence_embedding, skill_embeddings)
            max_score, best_match_idx = similarities.max().item(), similarities.argmax().item()

            if max_score > threshold:
                matched_skill = skill_tags[best_match_idx]
                if matched_skill.lower() in sentence.lower():
                    detected_skills.add(matched_skill)

    return list(detected_skills)

@app.route("/upload-resume", methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['resume']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported."}), 400

    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    detected_skills = extract_skills_from_text(text, skill_tagss)
    gmail_matches = re.findall(r'[\w\.-]+@gmail\.com', text)
    email_found = gmail_matches[0] if gmail_matches else None

    if email_found:
        user_doc = collection.find_one({"email": email_found})
        if user_doc:
            existing_skills = user_doc.get("skills", [])
            merged_skills = list(set(existing_skills + detected_skills))
            collection.update_one({"email": email_found}, {"$set": {"skills": merged_skills}})

    return jsonify({"filename": file.filename, "detected_skills": detected_skills, "extracted_email": email_found})

def fetch_jobs():
    URL = "https://aijobs.net/"
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    job_links = soup.find_all('a', class_='col py-2', href=True)
    jobs = []

    for job_link in job_links:
        link = "https://aijobs.net" + job_link.get('href')
        location = job_link.find('span', class_='d-none d-md-block text-break mb-1') or job_link.find('span', class_='d-block d-md-none text-break mb-1')
        location = location.get_text(strip=True) if location else "Not specified"

        employment_type = job_link.find('span', class_='badge rounded-pill text-bg-secondary my-md-1 ms-1')
        employment_type = employment_type.get_text(strip=True) if employment_type else "Not specified"

        experience_level = job_link.find('span', class_='badge rounded-pill text-bg-info my-md-1 d-none d-md-inline-block') or job_link.find('span', class_='badge rounded-pill text-bg-info my-md-1 d-md-none')
        experience_level = experience_level.get_text(strip=True) if experience_level else "Not specified"

        salary_div = job_link.find('div', class_='d-block mb-4')
        salary = salary_div.find('span', class_='badge rounded-pill text-bg-success d-none d-md-inline-block') or salary_div.find('span', class_='badge rounded-pill text-bg-success d-md-none') if salary_div else None
        salary = salary.get_text(strip=True) if salary else "Not specified"

        company_span = job_link.find('span', class_='text-muted')
        company = company_span.get_text(strip=True).split('Remote-first')[0].replace('\xa0', ' ').strip() if company_span else "Not specified"

        h5_element = job_link.find('h5', class_='fw-normal text-body-emphasis text-break')
        title = h5_element.get_text(strip=True).split('Featured')[0].replace('\xa0', ' ').strip() if h5_element else "Not specified"

        skill_tags = [span.get_text(strip=True) for span in job_link.find_all('span', class_='badge rounded-pill text-bg-light') if not span.get_text(strip=True).startswith('+')]
        benefit_tags = [sibling.get_text(strip=True) for sibling in job_link.find_all('span', class_='badge text-bg-success') if not sibling.get_text(strip=True).startswith('+')]

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'employment_type': employment_type,
            'experience_level': experience_level,
            'salary': salary,
            'skill_tags': ', '.join(skill_tags) if skill_tags else 'No skills listed',
            'benefit_tags': ', '.join(benefit_tags) if benefit_tags else 'No benefits listed',
            'link': link
        })
    return jobs

def create_email_content(job_list):
    if not job_list:
        return "No new AI/ML/NLP job opportunities found today."

    message = "*Your Daily AI/ML/NLP Job Alerts*\n\n"
    for job in job_list:
        message += f"🔹 **{job['title']}** at *{job['company']}* ({job['location']})\n"
        message += f"   • Employment Type: {job['employment_type']}\n"
        message += f"   • Experience Level: {job['experience_level']}\n"
        message += f"   • Salary: {job['salary']}\n"
        message += f"   • Required Skills: {job['skill_tags']}\n"
        message += f"   • Benefits: {job['benefit_tags']}\n"
        message += f"   • Apply here 👉 {job['link']}\n"
        message += f"{'-'*60}\n\n"
    return message + "🚀 Stay tuned — new opportunities coming your way soon!"

def mains():
    jobs = fetch_jobs()
    users = list(collection.find({}, {'_id': 0}))
    EMAIL_USER = 'pramodhdusa3720@gmail.com'
    EMAIL_PASS = 'xjky ntcz jmzq hizl'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)

    for user in users:
        email = user['email']
        user_skills = [skill.lower() for skill in user.get('skills', [])]
        history = user.get('history', [])

        for job in jobs:
            combined_text = f"{job['title']} {job['skill_tags']}".lower().replace(' ', '')
            if any(skill in combined_text for skill in user_skills) and job['title'] not in history:
                msg = EmailMessage()
                msg['Subject'] = "🔥 Your Personalized AI Job Alert"
                msg['From'] = EMAIL_USER
                msg['To'] = email
                msg.set_content(create_email_content([job]))
                server.send_message(msg)
                collection.update_one({"email": email}, {"$addToSet": {"history": job['title']}})
                break
    server.quit()
    print("✅ Job alert emails sent.")

scheduler = BackgroundScheduler()
scheduler.add_job(mains, 'cron', hour=16, minute=55)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)










##backup----------------

# from flask import Flask, request, jsonify
# # from flask_jwt_extended import create_access_token
# # from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
# # from dotenv import load_dotenv
# import schedule
# import time
# from apscheduler.schedulers.background import BackgroundScheduler
# from sentence_transformers import SentenceTransformer, util
# import pdfplumber
# import re 
# from flask_cors import CORS
# import pymongo
# from datetime import datetime
# import os
# import spacy

# #
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd

# import smtplib
# from email.message import EmailMessage
# #

# # load_dotenv()
# app = Flask(__name__)
# # app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
# # jwt = JWTManager(app)
# CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# model = SentenceTransformer('all-MiniLM-L6-v2')


# # ✅ MongoDB connection using pymongo directly
# MONGO_URI = "mongodb+srv://smartjob:smartjob123@cluster0.hjj7k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # Initialize MongoDB client
# try:
#     client = pymongo.MongoClient(MONGO_URI)
#     # Test the connection
#     client.admin.command('ping')
#     print("✅ MongoDB connected successfully.")
    
#     # Get database and collection
#     db = client['smartjob_db'] 
#     collection = db['skills']
    
# except Exception as e:
#     print("❌ MongoDB connection failed:", e)
#     client = None

# #------------#signup
# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')  

#     # Check if user already exists by email
#     if collection.find_one({"email": email}):
#         return jsonify({"error": "Email already exists"}), 400

#     # Insert new user document
#     new_user = {
#         "username": username,
#         "email": email,
#         "password": password,
#         "skills": [],
#         "history": [], 
#     }
#     collection.insert_one(new_user)
#     # access_token = create_access_token(identity=email)
#     return jsonify({"message": "User registered successfully"}), 201

# #-------------#signupend



# #------------#predict(skills submit)
# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         data = request.json
#         email = data.get("email")
#         new_skills = data.get("skills", [])

#         if not email:
#             return jsonify({"error": "Email is required"}), 400
#         if not new_skills:
#             return jsonify({"error": "No skills provided"}), 400

#         print(f"Updating skills for {email}: {new_skills}")

#         # Fetch existing skills for user
#         user = collection.find_one({"email": email})

#         if not user:
#             return jsonify({"error": "User not found"}), 404

#         existing_skills = user.get("skills", [])

#         # Merge existing and new skills, avoid duplicates
#         combined_skills = list(set(existing_skills + new_skills))

#         # Update user with combined skills
#         result = collection.update_one(
#             {"email": email},
#             {"$set": {"skills": combined_skills}}
#         )

#         return jsonify({
#             "status": "success",
#             "updated_skills": combined_skills,
#             "message": f"Skills updated for {email}"
#         })

#     except Exception as e:
#         print("Error in predict route:", e)
#         return jsonify({
#             "error": "Internal server error",
#             "message": str(e)
#         }), 500


# #-----#predict(skills-end)

# #-----#upload-resume

# skill_tagss = [
#     "machine learning", "ML", "deep learning", "NLP", "natural language processing",
#      "computer vision", "CV", "data analysis", "data analytics", "EDA",
#      "web development", "full stack development", "software engineering",
#      "cloud computing", "AWS", "Azure", "React", "React.js", "Node", "Node.js",
#      "Big Data", "Bigdata", "generative ai", "TensorFlow", "PyTorch", "SQL", "MongoDB"
# ]

# def extract_skills_from_text(text, skill_tags, threshold=0.65):  # Increased threshold
#     # Better text preprocessing
#     text = re.sub(r'\s+', ' ', text).lower()
#     sentences = [s.strip() for s in re.split(r'[.,;\n•\-–()]', text) if len(s.strip()) > 10]  # Skip short fragments
    
#     skill_embeddings = model.encode([s.lower() for s in skill_tags])
#     detected_skills = set()

#     # First pass: Exact matching (case insensitive)
#     for skill in skill_tags:
#         if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text.lower()):
#             detected_skills.add(skill)

#     # Second pass: Semantic matching only for longer sentences
#     for sentence in sentences:
#         if len(sentence.split()) > 3:  # Only analyze meaningful sentences
#             sentence_embedding = model.encode(sentence)
#             similarities = util.cos_sim(sentence_embedding, skill_embeddings)
#             max_score, best_match_idx = similarities.max().item(), similarities.argmax().item()
            
#             if max_score > threshold:
#                 matched_skill = skill_tags[best_match_idx]
#                 # Additional validation - skill should appear in sentence
#                 if matched_skill.lower() in sentence.lower():
#                     detected_skills.add(matched_skill)

#     return list(detected_skills)


# # Route to handle resume upload and analysis
# @app.route("/upload-resume", methods=['POST'])
# def upload_resume():
#     if 'resume' not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request.files['resume']

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if not file.filename.endswith('.pdf'):
#         return jsonify({"error": "Only PDF files are supported."}), 400

#     # Extract text from PDF directly without saving
#     text = ""
#     with pdfplumber.open(file) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"

#     # Extract skill tags from resume text
#     detected_skills = extract_skills_from_text(text, skill_tagss)
#     print("Detected Skills:", detected_skills)

#     # Extract Gmail address
#     gmail_matches = re.findall(r'[\w\.-]+@gmail\.com', text)
#     email_found = gmail_matches[0] if gmail_matches else None
#     print("Extracted Email:", email_found)

#     # If email found, merge skills with DB
#     if email_found:
#         user_doc = collection.find_one({"email": email_found})

#         if user_doc:
#             existing_skills = user_doc.get("skills", [])
#             merged_skills = list(set(existing_skills + detected_skills))

#             results = collection.update_one(
#                 {"email": email_found},
#                 {"$set": {"skills": merged_skills}}
#             )
#             print(f"Updated skills for {email_found}: {merged_skills}")
#         else:
#             print(f"No user found with email: {email_found}")

#     return jsonify({
#         "filename": file.filename,
#         "detected_skills": detected_skills,
#         "extracted_email": email_found
#     })

# #---------#upload resume end



# def fetch_jobs():
#     URL = "https://aijobs.net/"
#     page = requests.get(URL)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     job_links = soup.find_all('a', class_='col py-2', href=True)

#     jobs = []

#     for job_link in job_links:
#         link = "https://aijobs.net" + job_link.get('href')
#         location = "Not specified"
#         employment_type = "Not specified"
#         experience_level = "Not specified"
#         salary = "Not specified"
#         title = "Not specified"
#         company = "Not specified"

#         location_desktop = job_link.find('span', class_='d-none d-md-block text-break mb-1')
#         location_mobile = job_link.find('span', class_='d-block d-md-none text-break mb-1')

#         if location_desktop:
#             location = location_desktop.get_text(strip=True)
#         elif location_mobile:
#             location = location_mobile.get_text(strip=True)

#         employment_span = job_link.find('span', class_='badge rounded-pill text-bg-secondary my-md-1 ms-1')
#         if employment_span:
#             employment_type = employment_span.get_text(strip=True)

#         exp_desktop = job_link.find('span', class_='badge rounded-pill text-bg-info my-md-1 d-none d-md-inline-block')
#         exp_mobile = job_link.find('span', class_='badge rounded-pill text-bg-info my-md-1 d-md-none')

#         if exp_desktop:
#             experience_level = exp_desktop.get_text(strip=True)
#         elif exp_mobile:
#             experience_level = exp_mobile.get_text(strip=True)

#         salary_div = job_link.find('div', class_='d-block mb-4')
#         if salary_div:
#             salary_desktop = salary_div.find('span', class_='badge rounded-pill text-bg-success d-none d-md-inline-block')
#             salary_mobile = salary_div.find('span', class_='badge rounded-pill text-bg-success d-md-none')

#             if salary_desktop:
#                 salary = salary_desktop.get_text(strip=True)
#             elif salary_mobile:
#                 salary = salary_mobile.get_text(strip=True)

#         company_span = job_link.find('span', class_='text-muted')
#         if company_span:
#             company_text = company_span.get_text(strip=True)
#             company = company_text.split('Remote-first')[0].replace('\xa0', ' ').strip()

#         h5_element = job_link.find('h5', class_='fw-normal text-body-emphasis text-break')
#         if h5_element:
#             title_text = h5_element.get_text(strip=True)
#             title = title_text.split('Featured')[0].replace('\xa0', ' ').strip()

#         skill_tags = []
#         skill_spans = job_link.find_all('span', class_='badge rounded-pill text-bg-light')
#         for span in skill_spans:
#             tag_text = span.get_text(strip=True)
#             if not tag_text.startswith('+'):
#                 skill_tags.append(tag_text)

#         benefit_tags = []
#         br_tag = job_link.find('br')
#         if br_tag:
#             for sibling in br_tag.find_next_siblings():
#                 if sibling.name == 'span' and 'badge' in sibling.get('class', []) and 'text-bg-success' in sibling.get('class', []):
#                     tag_text = sibling.get_text(strip=True)
#                     if not tag_text.startswith('+'):
#                         benefit_tags.append(tag_text)

#         jobs.append({
#             'title': title,
#             'company': company,
#             'location': location,
#             'employment_type': employment_type,
#             'experience_level': experience_level,
#             'salary': salary,
#             'skill_tags': ', '.join(skill_tags) if skill_tags else 'No skills listed',
#             'benefit_tags': ', '.join(benefit_tags) if benefit_tags else 'No benefits listed',
#             'link': link
#         })

#     return jobs


# def create_email_content(job_list):
#     if not job_list:
#         return "No new AI/ML/NLP job opportunities found today."

#     message = "*Your Daily AI/ML/NLP Job Alerts*\n\n"
#     for job in job_list:
#         message += f"🔹 **{job['title']}** at *{job['company']}* ({job['location']})\n"
#         message += f"   • Employment Type: {job['employment_type']}\n"
#         message += f"   • Experience Level: {job['experience_level']}\n"
#         message += f"   • Salary: {job['salary']}\n"
#         message += f"   • Required Skills: {job['skill_tags']}\n"
#         message += f"   • Benefits: {job['benefit_tags']}\n"
#         message += f"   • Apply here 👉 {job['link']}\n"
#         message += f"{'-'*60}\n\n"

#     message += "🚀 Stay tuned — new opportunities coming your way soon!"
#     return message


# def mains():
#     jobs = fetch_jobs()
#     users = list(collection.find({}, {'_id': 0}))

#     EMAIL_USER = 'pramodhdusa3720@gmail.com'
#     EMAIL_PASS = 'xjky ntcz jmzq hizl'

#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(EMAIL_USER, EMAIL_PASS)

#     for user in users:
#         email = user['email']
#         user_skills = [skill.lower() for skill in user.get('skills', [])]
#         history = user.get('history', [])

#         for job in jobs:
#             combined_text = f"{job['title']} {job['skill_tags']}".lower().replace(' ', '')

#             if any(skill in combined_text for skill in user_skills) and job['title'] not in history:
#                 msg = EmailMessage()
#                 msg['Subject'] = "🔥 Your Personalized AI Job Alert"
#                 msg['From'] = EMAIL_USER
#                 msg['To'] = email
#                 msg.set_content(create_email_content([job]))

#                 server.send_message(msg)
#                 print(f"✅ Email sent to {email} with job: {job['title']}")

#                 collection.update_one(
#                     {"email": email},
#                     {"$addToSet": {"history": job['title']}}
#                 )

#                 break
#         else:
#             print(f"ℹ️ No new matching jobs for {email}")

#     server.quit()
#     print("✅ All job alert emails sent successfully.")


# # Scheduler setup
# scheduler = BackgroundScheduler()
# scheduler.add_job(mains, 'cron', hour=16, minute=55)
# scheduler.start()

# print("🔄 Scheduler started, will run main() every day at 10:58 PM.")



# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)


#----#