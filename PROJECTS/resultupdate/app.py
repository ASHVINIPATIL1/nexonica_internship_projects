from flask import Flask, render_template, request, session, redirect, url_for, flash
import re
from PyPDF2 import PdfReader
import os

app = Flask(__name__)
app.secret_key = 'myKEY3000'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # Get students from session (will be empty on restart)
    students = session.get('students', [])
    
    # Calculate statistics
    stats = {
        'total': len(students),
        'pass': len([s for s in students if s.get('status') == 'Pass']),
        'atkt': len([s for s in students if s.get('status') == 'ATKT']),
        'fail': len([s for s in students if s.get('status') == 'Fail']),
        'with_backlogs': len([s for s in students if s.get('backlogs', 0) > 0])
    }
    
    return render_template('index.html', students=students, stats=stats)

@app.route('/upload', methods=['POST'])
def upload():
    # Check if file was uploaded
    if 'pdf' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['pdf']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not file.filename.endswith('.pdf'):
        flash('Please upload a PDF file', 'error')
        return redirect(url_for('index'))
    
    # Save file temporarily
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    try:
        # Read PDF
        reader = PdfReader(filepath)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        # Extract students
        new_students = extract_multiple_students(pdf_text)
        
        if not new_students:
            flash('No valid student data found in PDF', 'error')
            os.remove(filepath)
            return redirect(url_for('index'))
        
        # Check for duplicates
        existing_students = session.get('students', [])
        unique_students, duplicates = check_duplicates(new_students, existing_students)
        
        # Add to session
        if 'students' not in session:
            session['students'] = []
        
        session['students'].extend(unique_students)
        session.modified = True
        
        # Delete uploaded file
        os.remove(filepath)
        
        # Show message
        if unique_students and duplicates:
            flash(f'Added {len(unique_students)} student(s). Skipped {len(duplicates)} duplicate(s).', 'warning')
        elif unique_students:
            flash(f'Successfully added {len(unique_students)} student(s)', 'success')
        elif duplicates:
            flash(f'All {len(duplicates)} student(s) were duplicates.', 'info')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

def extract_multiple_students(pdf_text):
    """Extract data from multiple students PDF"""
    students = []
    
    # Split by student records
    pattern = r'PRN:\s*(\w+)\s+SEAT NO\.:\s*([A-Z]\d{9})\s+NAME:\s*([A-Z\s]+?)\s+Mother\'s Name\s*:-\s*([A-Z\s]+?)(?=\s+SEMESTER|\s+Third|\s+Fourth|\s+PRN:)'
    student_blocks = re.split(pattern, pdf_text)
    
    # Try alternative pattern if first doesn't work
    if len(student_blocks) < 5:
        pattern = r'PRN:\s*(\w+)\s+SEAT\s*NO\.?:\s*([A-Z]\d{9})\s+NAME:\s*([A-Z\s]+?)\s+Mother[\'s\s]*Name\s*:?-?\s*([A-Z\s]+?)(?=\s*SEMESTER|\s*Third|\s*Fourth|\s*PRN:)'
        student_blocks = re.split(pattern, pdf_text, flags=re.IGNORECASE)
    
    # Process each student
    for i in range(1, len(student_blocks), 5):
        if i + 3 >= len(student_blocks):
            break
        
        try:
            prn = student_blocks[i].strip()
            seat_no = student_blocks[i + 1].strip()
            student_name = student_blocks[i + 2].strip()
            mother_name = student_blocks[i + 3].strip()
            data_block = student_blocks[i + 4] if i + 4 < len(student_blocks) else ""
            
            student = {
                'prn': prn,
                'seat_no': seat_no,
                'student_name': student_name,
                'mother_name': mother_name,
                'sgpa3': 'N/A',
                'sgpa4': 'N/A',
                'credits': 'N/A',
                'credits_earned': '0',
                'credits_total': '0',
                'status': 'Unknown',
                'backlogs': 0
            }
            
            # Extract SGPAs
            sgpa3_match = re.search(r"Third\s+Semester\s+SGPA\s*:?\s*(\d+\.\d{2}|-{2,})", data_block, re.IGNORECASE)
            if sgpa3_match:
                student['sgpa3'] = sgpa3_match.group(1)
            
            sgpa4_match = re.search(r"Fourth\s+Semester\s+SGPA\s*:?\s*(\d+\.\d{2}|-{2,})", data_block, re.IGNORECASE)
            if sgpa4_match:
                student['sgpa4'] = sgpa4_match.group(1)
            
            # Extract credits
            credit_match = re.search(r"SECOND YEAR Total Credits Earned :?\s*(\d+)\s*/\s*(\d+)", data_block, re.IGNORECASE)
            if credit_match:
                student['credits_earned'], student['credits_total'] = credit_match.groups()
                student['credits'] = f"{student['credits_earned']}/{student['credits_total']}"
            
            # Status
            if re.search(r"Result\s*:?\s*Fail", data_block, re.IGNORECASE):
                student['status'] = "Fail"
            elif re.search(r"A\.?T\.?K\.?T\.?|ATKT", data_block, re.IGNORECASE):
                student['status'] = "ATKT"
            elif re.search(r"(Total|Second\s+Year)\s+Credits\s+Earned", data_block, re.IGNORECASE):
                student['status'] = "Pass"
            
            # Backlogs
            student['backlogs'] = len(re.findall(r'\bFFF\b', data_block))
            
            students.append(student)
            
        except:
            continue
    
    return students

def check_duplicates(new_students, existing_students):
    """Check for duplicate PRNs"""
    existing_prns = {s.get('prn') for s in existing_students}
    unique = []
    duplicates = []
    
    for student in new_students:
        prn = student.get('prn')
        if prn in existing_prns:
            duplicates.append(student)
        else:
            unique.append(student)
            existing_prns.add(prn)
    
    return unique, duplicates

@app.route('/sort', methods=['POST'])
def sort_students():
    """Sort students"""
    sort_by = request.form.get('sort_by', 'name')
    order = request.form.get('order', 'asc')
    
    students = session.get('students', [])
    
    if sort_by == 'name':
        students.sort(key=lambda x: x.get('student_name', ''), reverse=(order == 'desc'))
    elif sort_by == 'sgpa':
        def get_sgpa(s):
            sgpa3 = s.get('sgpa3', '0')
            if sgpa3 in ['N/A', '-----', None]:
                return 0.0
            try:
                return float(sgpa3.replace('-', '0'))
            except:
                return 0.0
        students.sort(key=get_sgpa, reverse=(order == 'desc'))
    elif sort_by == 'backlogs':
        students.sort(key=lambda x: int(x.get('backlogs', 0)), reverse=(order == 'desc'))
    elif sort_by == 'credits':
        students.sort(key=lambda x: int(x.get('credits_earned', '0')), reverse=(order == 'desc'))
    
    session['students'] = students
    session.modified = True
    
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    """Search students"""
    query = request.form.get('query', '').lower()
    
    if not query:
        return redirect(url_for('index'))
    
    all_students = session.get('students', [])
    filtered = [s for s in all_students 
                if query in s.get('student_name', '').lower() 
                or query in s.get('seat_no', '').lower() 
                or query in s.get('prn', '').lower()]
    
    stats = {
        'total': len(filtered),
        'pass': len([s for s in filtered if s.get('status') == 'Pass']),
        'atkt': len([s for s in filtered if s.get('status') == 'ATKT']),
        'fail': len([s for s in filtered if s.get('status') == 'Fail']),
        'with_backlogs': len([s for s in filtered if s.get('backlogs', 0) > 0])
    }
    
    return render_template('index.html', students=filtered, stats=stats, search_query=query)

@app.route('/clear', methods=['POST'])
def clear():
    """Clear all data"""
    session.pop('students', None)
    flash('All data cleared', 'info')
    return redirect(url_for('index'))

@app.route('/delete/<prn>', methods=['POST'])
def delete_student(prn):
    """Delete single student"""
    students = session.get('students', [])
    session['students'] = [s for s in students if s.get('prn') != prn]
    session.modified = True
    flash('Student deleted', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)