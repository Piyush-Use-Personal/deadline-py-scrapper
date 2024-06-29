import pandas as pd
import re

def is_malicious(entry):
    # Example: Simple regex to identify SQL injection attempts
    sql_injection_patterns = [
        re.compile(r"(\%27)|(\')|(\-\-)|(\%23)|(#)"),
        re.compile(r"(\%22)|(\")|(\%3D)|(=)|(\%3C)|(<)|(\%3E)|(>)"),
    ]
    for pattern in sql_injection_patterns:
        if pattern.search(entry):
            return True
    return False

def process_data(data):
    malicious_entries = []
    for entry in data:
        if is_malicious(entry):
            malicious_entries.append(entry)
    return malicious_entries

def save_to_csv(entries, filename='malicious_entries.csv'):
    df = pd.DataFrame(entries, columns=['Malicious Entry'])
    df.to_csv(filename, index=False)
