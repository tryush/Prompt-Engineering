import openai
import pandas as pd
import numpy as np
import json
from multiprocessing import Pool 
import pickle
import datetime
import re
import time
import joblib


openai.api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

df_notes = pd.read_excel("charts.xlsx")

import tiktoken
enc = tiktoken.get_encoding("cl100k_base")

def fun(x):
    encoded = enc.encode(x)
    if len(encoded) > 3300:
        return enc.decode(encoded[:3300])
    
    return x

df_notes.columns

df_notes['ClinicalNotes_req'] = df_notes['ClinicalNotes_req'].apply(lambda x: fun(x))
df_notes['ClinicalNotes_req'] = df_notes['ClinicalNotes_req'].apply(lambda x: re.sub(r'_x000D_', '', x))


df_fin = df_notes.copy()

id_list = df_fin['ID'].to_list()
clinicalnotes_list = df_fin['ClinicalNotes_req'].to_list()
target_list = df_fin['target'].to_list()
inputs = []

len(clinicalnotes_list), len(id_list)

for clinicalnotes, vns in zip(clinicalnotes_list, id_list):
    prompt = f"""You will be provided a medical text chart delimited by triple backticks. Your task is to provide the response in JSON format with the following key:
predicted_category: <category>
Where 'category' is the response to the question.

question: Indicate the category of the medical chart by selecting one of the following options: 'Splint', 'Laceration', 'Cerumen', or 'Other'.
```{clinicalnotes}```"""
    inputs.append((prompt, vns))

def fetch_response(inputs):
    prompt = inputs[0]
    vn = inputs[1]
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a trained clinical notes specialist"},
        {"role": "user", "content": prompt}
    ], temperature = 1)
    return {'vn':vn, 'response': completion.choices[0].message['content']}

i = 0
for inpt in inputs[0:]:
    print("\r {}".format(i), end="")
    response = fetch_response(inpt)
    time.sleep(2)
    joblib.dump(response, "/category/file_{}.pkl".format(i))
    i+=1

dir_path = "/category/"
files = os.listdir(dir_path)

len(files)

dict_list = []

for file_name in files:
    if file_name.endswith('.pkl'):
        with open(os.path.join(dir_path, file_name), 'rb') as f:
            dictionary = pickle.load(f)
            dict_list.append(dictionary)

df = pd.DataFrame(dict_list)
df.rename(columns = {"vn":"ID"}, inplace = True)

df['pred_category'] = df['response'].apply(lambda x: x.split(":")[1])

df['pred_category'] = df['pred_category'].str.split("""['',~`_ '\'/'\n'{}""]""")
def regex_expr_simple(x):
    lst = []
    for i in x:
        if i != '' :
            lst.append(i)
    return " ".join(lst)

df['pred_category'] = df['pred_category'].apply(lambda x : regex_expr_simple(x))
df.head()

df['pred_category'].value_counts()

def my_fun2(txt):
    if txt not in ["Cerumen","Laceration","Other","Splint"]:
        return "Other"
    else:
        return txt

df['pred_category'] = df['pred_category'].apply(my_fun2)

df['pred_category'].value_counts()

df.head(4)

df.to_excel("/category/response_category.xlsx",index=False)
