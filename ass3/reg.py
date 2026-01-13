import argparse
import re

v1 = "car MH 15 KF 1234 num."
pattern = "[A-Z]{2}\s[0-9]{2}\s[A-Z]{2}\s[0-9]{4}\s"
result = re.findall(pattern, v1)

if len(result) > 0:
    print(result)
else:
    print("not found")