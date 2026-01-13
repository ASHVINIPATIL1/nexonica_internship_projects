from flask import Flask, render_template, request, session, redirect, url_for, flash
import re
from PyPDF2 import PdfReader
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'myKEY3000'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def add_missing_fields(students):
    """Make sure every student has all required fields"""
    for student in students:
        # If a field is missing, add it with a default value
        if 'seat_no' not in student:
            student['seat_no'] = 'Not found'
        if 'prn' not in student:
            student['prn'] = 'Not found'
        if 'student_name' not in student:
            student['student_name'] = 'Not found'
        if 'mother_name' not in student:
            student['mother_name'] = 'Not found'
        if 'sgpa3' not in student:
            student['sgpa3'] = 'N/A'
        if 'sgpa4' not in student:
            student['sgpa4'] = 'N/A'
        if 'credits' not in student:
            student['credits'] = 'N/A'
        if 'status' not in student:
            student['status'] = 'Unknown'
        if 'backlogs' not in student:
            student['backlogs'] = 0
    
    return students

def find_duplicates(new_students, old_students):
    """Check if students already exist based on PRN and Seat Number"""
    # Get all PRNs and Seat Numbers that already exist
    existing_prns = set()
    existing_seats = set()
    
    for student in old_students:
        prn = str(student.get('prn', '')).strip()
        seat = str(student.get('seat_no', '')).strip()
        if prn and prn != 'Not found' and prn != 'None':
            existing_prns.add(prn)
        if seat and seat != 'Not found' and seat != 'None':
            existing_seats.add(seat)
    
    # Separate new students into unique and duplicates
    unique = []
    duplicates = []
    
    for student in new_students:
        prn = str(student.get('prn', '')).strip()
        seat = str(student.get('seat_no', '')).strip()
        
        # Check if duplicate by PRN or Seat Number
        is_duplicate = False
        if prn and prn != 'Not found' and prn != 'None' and prn in existing_prns:
            is_duplicate = True
        elif seat and seat != 'Not found' and seat != 'None' and seat in existing_seats:
            is_duplicate = True
        
        if is_duplicate:
            duplicates.append(student)
        else:
            unique.append(student)
            if prn and prn != 'Not found' and prn != 'None':
                existing_prns.add(prn)
            if seat and seat != 'Not found' and seat != 'None':
                existing_seats.add(seat)
    
    return unique, duplicates

def save_undo_history():
    """Save current state so we can undo later"""
    if 'students' not in session:
        return
    
    if 'history' not in session:
        session['history'] = []
    
    # Save current state
    session['history'].append({
        'students': session['students'].copy(),
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 10 states
    if len(session['history']) > 10:
        session['history'].pop(0)
    
    session.modified = True

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def index():
    """Main page - shows all students in a table"""
    # Get students from session
    students = session.get('students', [])
    students = add_missing_fields(students)
    
    # Calculate statistics
    total = len(students)
    passed = 0
    atkt = 0
    failed = 0
    with_backlogs = 0
    
    for student in students:
        if student.get('status') == 'Pass':
            passed += 1
        elif student.get('status') == 'ATKT':
            atkt += 1
        elif student.get('status') == 'Fail':
            failed += 1
        
        if student.get('backlogs', 0) > 0:
            with_backlogs += 1
    
    stats = {
        'total': total,
        'pass': passed,
        'atkt': atkt,
        'fail': failed,
        'with_backlogs': with_backlogs
    }
    
    # Get list of uploaded PDF files
    uploaded_files = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        for f in files:
            if f.endswith('.pdf'):
                uploaded_files.append(f)
    
    # Check if we can undo
    can_undo = len(session.get('history', [])) > 0
    
    return render_template('index.html', 
                         students=students, 
                         stats=stats,
                         uploaded_files=uploaded_files,
                         can_undo=can_undo)

@app.route('/upload', methods=['POST'])
def upload():
    """Handle PDF upload and extract student data"""
    
    # Check if file was uploaded
    if 'pdf' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('index'))
    
    file = request.files['pdf']
    pdf_type = request.form.get('pdf_type', 'single')  # single or multiple
    
    # Check if filename is empty
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Check if it's a PDF
    if not file.filename.endswith('.pdf'):
        flash('Please upload a PDF file', 'error')
        return redirect(url_for('index'))
    
    # Save file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Remove any path separators from filename for safety
    safe_name = os.path.basename(file.filename)
    filename = f"{timestamp}_{safe_name}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Read PDF
        reader = PdfReader(filepath)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        # Debug: Print first 500 characters of PDF text
        print(f"\n=== PDF TEXT SAMPLE (first 500 chars) ===")
        print(pdf_text[:500])
        print(f"=== PDF TYPE: {pdf_type} ===\n")
        
        # Extract student data based on type
        if pdf_type == 'single':
            new_students = extract_single_student(pdf_text)
        else:
            new_students = extract_multiple_students(pdf_text)
        
        print(f"=== EXTRACTED {len(new_students)} STUDENT(S) ===\n")
        
        # Check if we found any students
        if not new_students:
            flash('No valid student data found in PDF. Please check if the PDF format matches the expected format. Check VS Code terminal for details.', 'error')
            return redirect(url_for('index'))
        
        # Save current state for undo
        save_undo_history()
        
        # Check for duplicates
        existing_students = session.get('students', [])
        unique_students, duplicate_students = find_duplicates(new_students, existing_students)
        
        # Add unique students to session
        if 'students' not in session:
            session['students'] = []
        
        session['students'].extend(unique_students)
        session.modified = True
        
        # Show success message
        if unique_students and duplicate_students:
            flash(f'Added {len(unique_students)} student(s). Skipped {len(duplicate_students)} duplicate(s).', 'warning')
        elif unique_students:
            flash(f'Successfully added {len(unique_students)} student(s)', 'success')
        elif duplicate_students:
            flash(f'All {len(duplicate_students)} student(s) were duplicates.', 'info')
        
        # If single student, show detailed page
        if pdf_type == 'single' and len(unique_students) > 0:
            return render_template('single_result.html', student=unique_students[0])
        
        return redirect(url_for('index'))
        
    except Exception as e:
        import traceback
        print(f"\n=== ERROR OCCURRED ===")
        print(f"Error: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        print(f"=====================\n")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('index'))

# ============================================
# PDF EXTRACTION FUNCTIONS
# ============================================

def extract_single_student(pdf_text):
    """Extract data from a single student PDF"""
    
    # Create empty student with default values
    student = {
        'seat_no': 'Not found',
        'prn': 'Not found',
        'student_name': 'Not found',
        'mother_name': 'Not found',
        'sgpa3': 'N/A',
        'sgpa4': 'N/A',
        'credits': 'Not found',
        'credits_earned': '0',
        'credits_total': '0',
        'status': 'Unknown',
        'backlogs': 0
    }
    
    # Extract Seat Number
    seat_match = re.search(r"Seat No:\s*([A-Z]\d{9})", pdf_text, re.IGNORECASE)
    if seat_match:
        student['seat_no'] = seat_match.group(1)
    
    # Extract PRN
    prn_match = re.search(r"Perm Reg No\(PRN\):\s*(\w+)", pdf_text, re.IGNORECASE)
    if prn_match:
        student['prn'] = prn_match.group(1)
    
    # Extract Student Name
    name_match = re.search(r"Student Name:\s*([A-Z\s]+?)(?=\s+Mother Name:)", pdf_text, re.IGNORECASE)
    if name_match:
        student['student_name'] = name_match.group(1).strip()
    
    # Extract Mother Name
    mother_match = re.search(r"Mother Name:\s*([A-Z\s]+)", pdf_text, re.IGNORECASE)
    if mother_match:
        student['mother_name'] = mother_match.group(1).strip()
    
    # Check if it's First Year or Second Year PDF
    is_first_year = "First Semester SGPA" in pdf_text
    is_second_year = "Third Semester SGPA" in pdf_text
    
    if is_first_year:
        # Extract First Year SGPAs
        sgpa1_match = re.search(r"First Semester SGPA\s*:\s*(\d+\.\d{2}|-+)", pdf_text)
        if sgpa1_match:
            student['sgpa3'] = sgpa1_match.group(1)  # Use sgpa3 for display
        
        sgpa2_match = re.search(r"Second Semester SGPA\s*:\s*(\d+\.\d{2}|-+)", pdf_text)
        if sgpa2_match:
            student['sgpa4'] = sgpa2_match.group(1)  # Use sgpa4 for display
        
        # Extract First Year Credits
        credit_match = re.search(r"First Year Total Credits Earned\s*:\s*(\d+)/(\d+)", pdf_text)
        if credit_match:
            student['credits_earned'] = credit_match.group(1)
            student['credits_total'] = credit_match.group(2)
            student['credits'] = f"{credit_match.group(1)}/{credit_match.group(2)}"
    
    elif is_second_year:
        # Extract Second Year SGPAs
        sgpa3_match = re.search(r"Third Semester SGPA\s*:\s*(\d+\.\d{2}|-+)", pdf_text)
        if sgpa3_match:
            student['sgpa3'] = sgpa3_match.group(1)
        
        sgpa4_match = re.search(r"Fourth Semester SGPA\s*:\s*(\d+\.\d{2}|-+)", pdf_text)
        if sgpa4_match:
            student['sgpa4'] = sgpa4_match.group(1)
        
        # Extract Second Year Credits
        credit_match = re.search(r"(?:SECOND YEAR|Second Year) Total Credits Earned\s*:\s*(\d+)/(\d+)", pdf_text)
        if credit_match:
            student['credits_earned'] = credit_match.group(1)
            student['credits_total'] = credit_match.group(2)
            student['credits'] = f"{credit_match.group(1)}/{credit_match.group(2)}"
    
    # Determine Pass/Fail/ATKT Status
    if "Result : Fail" in pdf_text or "Result: Fail" in pdf_text:
        student['status'] = "Fail"
    elif "A.T.K.T." in pdf_text:
        student['status'] = "ATKT"
    else:
        student['status'] = "Pass"
    
    # Count backlogs (FFF = failed subjects)
    student['backlogs'] = len(re.findall(r'\bFFF\b', pdf_text))
    
    return [student]

def extract_multiple_students(pdf_text):
    """Extract data from multiple students PDF (college ledger)"""
    
    students = []
    
    # Simple approach: Split by "PRN:" to find each student
    # This is more flexible than complex regex patterns
    parts = re.split(r'PRN:\s*', pdf_text, flags=re.IGNORECASE)
    
    print(f"Found {len(parts)} parts when splitting by PRN:")
    
    # Skip first part (text before first PRN)
    for part in parts[1:]:
        try:
            # Extract PRN (first word after "PRN:")
            lines = part.split('\n')
            first_line = lines[0] if lines else ""
            prn_match = re.match(r'(\w+)', first_line.strip())
            if not prn_match:
                continue
            
            prn = prn_match.group(1).strip()
            
            # Extract Seat Number - look for "SEAT NO" or "SEAT NO."
            seat_match = re.search(r'SEAT\s+NO\.?:\s*([A-Z0-9]+)', part, re.IGNORECASE)
            seat_no = seat_match.group(1).strip() if seat_match else 'Not found'
            
            # Extract Name - look for "NAME:"
            name_match = re.search(r'NAME:\s*([A-Z\s]+?)(?=\s+Mother|\s+SEMESTER|\s+Third|\s+Fourth|$)', part, re.IGNORECASE)
            student_name = name_match.group(1).strip() if name_match else 'Not found'
            
            # Extract Mother Name - look for "Mother" or "Mother's Name"
            mother_match = re.search(r'Mother[\'s\s]*Name\s*:?-?\s*([A-Z\s]+?)(?=\s+SEMESTER|\s+Third|\s+Fourth|\s+PRN:|$)', part, re.IGNORECASE)
            mother_name = mother_match.group(1).strip() if mother_match else 'Not found'
            
            # Only add if we found at least PRN and Name
            if prn and student_name != 'Not found':
                # Create student dictionary
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
                
                # Extract Semester 3 SGPA
                sgpa3_match = re.search(r"Third\s+Semester\s+SGPA\s*:?\s*(\d+\.\d{2}|-{2,})", part, re.IGNORECASE)
                if sgpa3_match:
                    student['sgpa3'] = sgpa3_match.group(1)
                
                # Extract Semester 4 SGPA
                sgpa4_match = re.search(r"Fourth\s+Semester\s+SGPA\s*:?\s*(\d+\.\d{2}|-{2,})", part, re.IGNORECASE)
                if sgpa4_match:
                    student['sgpa4'] = sgpa4_match.group(1)
                
                # Extract Credits - try multiple patterns
                credit_patterns = [
                    r"Credits?\s+Earned\s*/?\s*Total\s*:?\s*(\d+)\s*/\s*(\d+)",
                    r"Total\s+Credits\s+Earned\s*:?\s*(\d+)\s*/\s*(\d+)",
                    r"Credits\s*:?\s*(\d+)\s*/\s*(\d+)",
                    r"Second\s+Year\s+Total\s+Credits\s+Earned\s*:?\s*(\d+)\s*/\s*(\d+)",
                ]
                credit_match = None
                for cp in credit_patterns:
                    credit_match = re.search(cp, part, re.IGNORECASE)
                    if credit_match:
                        break
                
                if credit_match:
                    student['credits_earned'] = credit_match.group(1)
                    student['credits_total'] = credit_match.group(2)
                    student['credits'] = f"{student['credits_earned']}/{student['credits_total']}"
                
                # Determine Status
                if "Result : Fail" in part or "Result: Fail" in part:
                    student['status'] = "Fail"
                elif "A.T.K.T." in part or "ATKT" in part:
                    student['status'] = "ATKT"
                elif "Total Credits Earned" in part or "Second Year Credits" in part or "Credits Earned" in part:
                    student['status'] = "Pass"
                
                # Count backlogs
                student['backlogs'] = len(re.findall(r'\bFFF\b', part))
                
                students.append(student)
                print(f"  - Extracted: {student_name} (PRN: {prn})")
            
        except Exception as e:
            print(f"  - Error processing student: {str(e)}")
            continue
    
    print(f"Total students extracted: {len(students)}\n")
    return students
    
    # Process each match
    for idx, match in enumerate(matches):
        try:
            prn = match.group(1).strip()
            seat_no = match.group(2).strip()
            student_name = match.group(3).strip()
            mother_name = match.group(4).strip()
            
            # Get the text block for this student (from this match to next match or end)
            start_pos = match.end()
            if idx + 1 < len(matches):
                end_pos = matches[idx + 1].start()
            else:
                end_pos = len(pdf_text)
            
            data_block = pdf_text[start_pos:end_pos]
            
            # Create student dictionary
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
            
            # Extract Semester 3 SGPA
            sgpa3_match = re.search(r"Third\s+Semester\s+SGPA\s*:?\s*(\d+\.\d{2}|-{2,})", data_block, re.IGNORECASE)
            if sgpa3_match:
                student['sgpa3'] = sgpa3_match.group(1)
            
            # Extract Semester 4 SGPA
            sgpa4_match = re.search(r"Fourth\s+Semester\s+SGPA\s*:?\s*(\d+\.\d{2}|-{2,})", data_block, re.IGNORECASE)
            if sgpa4_match:
                student['sgpa4'] = sgpa4_match.group(1)
            
            # Extract Credits - try multiple patterns
            credit_patterns = [
                r"Credits?\s+Earned\s*/?\s*Total\s*:?\s*(\d+)\s*/\s*(\d+)",
                r"Total\s+Credits\s+Earned\s*:?\s*(\d+)\s*/\s*(\d+)",
                r"Credits\s*:?\s*(\d+)\s*/\s*(\d+)",
                r"Second\s+Year\s+Total\s+Credits\s+Earned\s*:?\s*(\d+)\s*/\s*(\d+)",
            ]
            credit_match = None
            for cp in credit_patterns:
                credit_match = re.search(cp, data_block, re.IGNORECASE)
                if credit_match:
                    break
            
            if credit_match:
                student['credits_earned'] = credit_match.group(1)
                student['credits_total'] = credit_match.group(2)
                student['credits'] = f"{student['credits_earned']}/{student['credits_total']}"
            
            # Determine Status
            if "Result : Fail" in data_block or "Result: Fail" in data_block:
                student['status'] = "Fail"
            elif "A.T.K.T." in data_block or "ATKT" in data_block:
                student['status'] = "ATKT"
            elif "Total Credits Earned" in data_block or "Second Year Credits" in data_block or "Credits Earned" in data_block:
                student['status'] = "Pass"
            
            # Count backlogs
            student['backlogs'] = len(re.findall(r'\bFFF\b', data_block))
            
            students.append(student)
            
        except Exception as e:
            # Skip this student if there's an error
            continue
    
    return students

# ============================================
# UTILITY ROUTES
# ============================================

@app.route('/sort', methods=['POST'])
def sort_students():
    """Sort students by name, SGPA, backlogs, or credits"""
    
    sort_by = request.form.get('sort_by', 'name')
    order = request.form.get('order', 'asc')  # asc or desc
    
    students = session.get('students', [])
    students = add_missing_fields(students)
    
    # Sort based on selected field
    if sort_by == 'name':
        students.sort(key=lambda x: x.get('student_name', ''), reverse=(order == 'desc'))
    
    elif sort_by == 'sgpa':
        def get_sgpa_value(student):
            sgpa3 = student.get('sgpa3', '0')
            # Handle non-numeric values
            if sgpa3 in ['N/A', 'Not found', '-----', None]:
                return 0.0
            try:
                return float(sgpa3.replace('-', '0'))
            except:
                return 0.0
        
        students.sort(key=get_sgpa_value, reverse=(order == 'desc'))
    
    elif sort_by == 'backlogs':
        students.sort(key=lambda x: int(x.get('backlogs', 0)), reverse=(order == 'desc'))
    
    elif sort_by == 'credits':
        students.sort(key=lambda x: int(x.get('credits_earned', '0')), reverse=(order == 'desc'))
    
    # Save sorted list
    session['students'] = students
    session.modified = True
    
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    """Search for students by name, PRN, or seat number"""
    
    query = request.form.get('query', '').lower()
    
    if not query:
        return redirect(url_for('index'))
    
    all_students = session.get('students', [])
    all_students = add_missing_fields(all_students)
    
    # Filter students
    filtered_students = []
    for student in all_students:
        name = student.get('student_name', '').lower()
        seat = student.get('seat_no', '').lower()
        prn = student.get('prn', '').lower()
        backlogs = str(student.get('backlogs', '')).lower()
        
        if query in name or query in seat or query in prn or query in backlogs:
            filtered_students.append(student)
    
    # Calculate stats for filtered results
    total = len(filtered_students)
    passed = len([s for s in filtered_students if s.get('status') == 'Pass'])
    atkt = len([s for s in filtered_students if s.get('status') == 'ATKT'])
    failed = len([s for s in filtered_students if s.get('status') == 'Fail'])
    with_backlogs = len([s for s in filtered_students if s.get('backlogs', 0) > 0])
    
    stats = {
        'total': total,
        'pass': passed,
        'atkt': atkt,
        'fail': failed,
        'with_backlogs': with_backlogs
    }
    
    # Get uploaded files
    uploaded_files = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        for f in files:
            if f.endswith('.pdf'):
                uploaded_files.append(f)
    
    can_undo = len(session.get('history', [])) > 0
    
    return render_template('index.html', 
                         students=filtered_students, 
                         stats=stats, 
                         search_query=query,
                         uploaded_files=uploaded_files, 
                         can_undo=can_undo)

@app.route('/clear', methods=['POST'])
def clear():
    """Clear all student data"""
    save_undo_history()
    session.pop('students', None)
    flash('All student data cleared. You can undo this action.', 'info')
    return redirect(url_for('index'))

@app.route('/undo', methods=['POST'])
def undo():
    """Undo last action"""
    if 'history' in session and session['history']:
        # Get last saved state
        last_state = session['history'].pop()
        session['students'] = last_state['students']
        session.modified = True
        flash('Last action undone', 'success')
    else:
        flash('Nothing to undo', 'info')
    
    return redirect(url_for('index'))

@app.route('/delete/<prn>', methods=['POST'])
def delete_student(prn):
    """Delete a single student"""
    save_undo_history()
    
    students = session.get('students', [])
    initial_count = len(students)
    # Keep all students except the one with matching PRN
    session['students'] = [s for s in students if str(s.get('prn', '')).strip() != str(prn).strip()]
    session.modified = True
    
    if len(session['students']) < initial_count:
        flash('Student deleted.', 'success')
    else:
        flash('Student not found.', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete-file/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete an uploaded PDF file"""
    # Basic safety: only allow PDF files and remove path separators
    safe_filename = os.path.basename(filename)
    if not safe_filename.endswith('.pdf'):
        flash('Invalid filename', 'error')
        return redirect(url_for('index'))
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('File deleted', 'success')
    else:
        flash('File not found', 'error')
    
    return redirect(url_for('index'))

# ============================================
# RUN THE APP
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)