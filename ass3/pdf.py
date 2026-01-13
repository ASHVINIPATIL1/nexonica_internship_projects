import argparse
import re
from PyPDF2 import PdfReader

reader = PdfReader(r"C:\Users\acer\Downloads\ViewResult1.pdf")

pdf_text = ""
for page in reader.pages:
    pdf_text += page.extract_text() + "\n"

# Extract Seat No
seat_match = re.search(r"Seat No:\s*([A-Z]\d{9})", pdf_text)
if seat_match:
    print(f"{seat_match.group(0)}")
# Extract PRN
prn_match = re.search(r"Perm Reg No\(PRN\):\s*(\w+)", pdf_text)
if prn_match:
    print(f"{prn_match.group(0)}")
# Extract Name
name_match = re.search(r"Student Name:\s*([A-Za-z]+\s[A-Za-z]+\s[A-Za-z]+\s*)", pdf_text)
if name_match:
    print(f"{name_match.group(0)}")

#Extract Mother Name
mother_match = re.search(r"Mother Name:\s*([A-Za-z]+\s*)", pdf_text)
if mother_match:
    print(f"{mother_match.group(0)}")

#Extract first sem SGPA
sgpa1_match = re.search(r"First Semester SGPA :\s*(\d+\.\d{2})", pdf_text)
if sgpa1_match:
    print(f"{sgpa1_match.group(0)}")

#Extract second sem SGPA
sgpa2_match = re.search(r"Second Semester SGPA :\s*(\d+\.\d{2})", pdf_text)
if sgpa2_match:
    print(f"{sgpa2_match.group(0)}")

#Total Year Credits
credit_match = re.search(r"First Year Total Credits Earned :\s*(\d+\/\d+)", pdf_text)
if credit_match:
    print(f"{credit_match.group(0)}")
    #print(f"First Year Total Credits Earned: {credit_match.group(1)}"