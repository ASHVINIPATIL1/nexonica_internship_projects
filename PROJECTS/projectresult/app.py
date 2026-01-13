# from flask import Flask, render_template, request, session
# import re
# from PyPDF2 import PdfReader
# import os

# app = Flask(__name__)
# app.secret_key = 'myKEY3000'
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# @app.route('/')
# def index():
#     students = session.get('students', [])
#     return render_template('index.html', students=students)

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'pdf' not in request.files:
#         students = session.get('students', [])
#         return render_template('index.html', error='No file uploaded', students=students)
    
#     file = request.files['pdf']
    
#     if file.filename == '':
#         students = session.get('students', [])
#         return render_template('index.html', error='No file selected', students=students)
    
#     if file and file.filename.endswith('.pdf'):
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filepath)
        
#         # Your existing code
#         reader = PdfReader(filepath)
        
#         pdf_text = ""
#         for page in reader.pages:
#             pdf_text += page.extract_text() + "\n"
        
#         # Extract Seat No
#         seat_match = re.search(r"Seat No:\s*([A-Z]\d{9})", pdf_text)
#         if seat_match:
#             seat_no = seat_match.group(1)  
#         else:
#             seat_no = "Not found"
        
#         # Extract PRN
#         prn_match = re.search(r"Perm Reg No\(PRN\):\s*(\w+)", pdf_text)
#         if prn_match:
#             prn = prn_match.group(1)  
#         else:
#             prn = "Not found"
        
#         # Extract Name
#         name_match = re.search(r"Student Name:\s*([A-Za-z]+\s[A-Za-z]+\s[A-Za-z]+\s*)", pdf_text)
#         if name_match :
#             student_name = name_match.group(1).strip() 
#         else:
#             student_name = "Not found"
        
#         # Extract Mother Name
#         mother_match = re.search(r"Mother Name:\s*([A-Za-z]+\s*)", pdf_text)
#         if mother_match:
#             mother_name = mother_match.group(1).strip()  
#         else:
#             mother_mane = "Not found"
        
#         # Extract first sem SGPA
#         sgpa1_match = re.search(r"First Semester SGPA :\s*(\d+\.\d{2}|-+)", pdf_text)
#         if sgpa1_match:
#             sgpa1 = sgpa1_match.group(1) 
#         else:
#             sgpa1 = "Not found"
        
#         # Extract second sem SGPA
#         sgpa2_match = re.search(r"Second Semester SGPA :\s*(\d+\.\d{2}|-+)", pdf_text)
#         if sgpa2_match:
#             sgpa2 = sgpa2_match.group(1)  
#         else: 
#             sgpa2 = "Not found"
        
#         # Total Year Credits
#         credit_match = re.search(r"First Year Total Credits Earned :\s*(\d+\/\d+)", pdf_text)
#         if credit_match:
#             credits = credit_match.group(1)
#         else:
#             credits = "Not found"
        
#         # Delete uploaded file
#         os.remove(filepath)
        
#         # Add student data to session
#         if 'students' not in session:
#             session['students'] = []
        
#         student_data = {
#             'seat_no': seat_no,
#             'prn': prn,
#             'student_name': student_name,
#             'mother_name': mother_name,
#             'sgpa1': sgpa1,
#             'sgpa2': sgpa2,
#             'credits': credits
#         }
        
#         session['students'].append(student_data)
#         session.modified = True
        
#         return render_template('index.html', students=session['students'])
    
#     students = session.get('students', [])
#     return render_template('index.html', error='Please upload a PDF file', students=students)

# @app.route('/clear', methods=['POST'])
# def clear():
#     session.pop('students', None)
#     return render_template('index.html', students=[])

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, session
import re
from PyPDF2 import PdfReader
import os

app = Flask(__name__)
app.secret_key = 'myKEY3000'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    students = session.get('students', [])
    return render_template('index.html', students=students)

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        students = session.get('students', [])
        return render_template('index.html', error='No file uploaded', students=students)
    
    file = request.files['pdf']
    
    if file.filename == '':
        students = session.get('students', [])
        return render_template('index.html', error='No file selected', students=students)
    
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Your existing code
        reader = PdfReader(filepath)
        
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        # Extract Seat No
        seat_match = re.search(r"SEAT NO.:\s*([A-Z]\d{9})", pdf_text)
        if seat_match:
            seat_no = seat_match.group(1)  
        else:
            seat_no = "Not found"
        
        # Extract PRN
        prn_match = re.search(r"PRN:\s*(\w+)", pdf_text)
        if prn_match:
            prn = prn_match.group(1)  
        else:
            prn = "Not found"
        
        # Extract Name
        name_match = re.search(r"NAME:\s*([A-Za-z]+\s[A-Za-z]+\s[A-Za-z]+\s*)", pdf_text)
        if name_match :
            student_name = name_match.group(1).strip() 
        else:
            student_name = "Not found"
        
        # Extract Mother Name
        # mother_match = re.search(r"Mother's Name:\s*([A-Za-z]+\s*)", pdf_text)
        # if mother_match:
        #     mother_name = mother_match.group(1).strip()  
        # else:
        #     mother_mane = "Not found"
        
        # Extract first sem SGPA
        sgpa1_match = re.search(r"Third Semester SGPA :\s*(\d+\.\d{2}|-+)", pdf_text)
        if sgpa1_match:
            sgpa1 = sgpa1_match.group(1) 
        else:
            sgpa1 = "Not found"
        
        # Extract second sem SGPA
        sgpa2_match = re.search(r"Fourth Semester SGPA :\s*(\d+\.\d{2}|-+)", pdf_text)
        if sgpa2_match:
            sgpa2 = sgpa2_match.group(1)  
        else: 
            sgpa2 = "Not found"
        
        # Total Year Credits
        credit_match = re.search(r"SECOND YEAR Total Credits Earned :\s*(\d+\/\d+)", pdf_text)
        if credit_match:
            credits = credit_match.group(1)
        else:
            credits = "Not found"
        
        # Delete uploaded file
        os.remove(filepath)
        
        # Add student data to session
        if 'students' not in session:
            session['students'] = []
        
        student_data = {
            'seat_no': seat_no,
            'prn': prn,
            'student_name': student_name,
            # "mother's name": mother_name,
            'sgpa1': sgpa1,
            'sgpa2': sgpa2,
            'credits': credits
        }
        
        session['students'].append(student_data)
        session.modified = True
        
        return render_template('index.html', students=session['students'])
    
    students = session.get('students', [])
    return render_template('index.html', error='Please upload a PDF file', students=students)

@app.route('/clear', methods=['POST'])
def clear():
    session.pop('students', None)
    return render_template('index.html', students=[])

if __name__ == '__main__':
    app.run(debug=True)