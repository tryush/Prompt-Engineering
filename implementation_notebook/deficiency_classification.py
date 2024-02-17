import openai
import pandas as pd
import numpy as np
import json
from multiprocessing import Pool 
import pickle
import datetime
import re
import joblib
import time
from sklearn.metrics import confusion_matrix
import ast
openai.api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

df = pd.read_excel("/category/response_category.xlsx")

df_cerumen = df[(df['pred_category'] == 'Cerumen')]

df_cerumen.shape

df_cerumen['ClinicalNotes_req'] = df_cerumen['ClinicalNotes_req'].apply(lambda x: re.sub(r'_x000D_', '', x))

df_cerumen_sample = df_cerumen.sample(n = 10, random_state = 11)

id_list = df_cerumen_sample['ID'].to_list()
clinicalnotes_list = df_cerumen_sample['ClinicalNotes_req'].to_list()

cfinal = []
for clinicalnotes in clinicalnotes_list:
    prompt = f"""You are provided with a medical text chart. Your task is to check if the medical chart is deficient or not, based on the following steps:

Q1 Check If 'Cerumen Removal Procedure' is present in medical chart ?.

Q2 Check if 'Cerumen Removal' or 'ear irrigation' has been done ?.

Check below steps only if 'Cerumen Removal' or 'ear irrigation' has been done.

Q3 **Important**: Does the chart explicitly mentions that the cerumen removal procedure was performed under the supervision of a doctor? (Check for masked doctor names if used).

Q4 Check if cerumen removal method present or not ?, it can be similar to keywords like lavage, irrigation, or use of any instrument.

Q5 Check if any type of cerumen removal process is mentioned in the chart for 'one ear' or 'left ear' or 'right ear' or 'unilateral ear' or 'bilateral ears', etc.

Please provide answers in yes or not for all above questions.

If answers to above questions are all Yes then chart is non deficient else it is deficient

You need to ouput a list with following format: [response of Q1, response of Q2, response of Q3, response of Q4, response of Q5, Chart is deficient or not] and each element of list should not be more than 2 words.

medical chart information is below
{clinicalnotes}
"""
    cfinal.append(prompt)

def get_completion(prompt, model = 'gpt-3.5-turbo'):
    messages = [{"role": "system", "content": "You are a trained medical chart specialist"},
                {"role":"user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0.4
    )
    return response['choices'][0]['message']['content']

out = []
for i in range(len(cfinal)):
    print("chart number:", i)
    res=get_completion(cfinal[i])
    vis=id_list[i]
    out.append([vis,res])
    time.sleep(3)

df_cerumen_sample[['ID', 'target']]

import joblib
joblib.dump(out, "/data/out_v8.pkl")

out = joblib.load("/data/out_v8.pkl")

columns = {
    'ID': [],
    'Q1': [],
    'Q2': [],
    'Q3': [],
    'Q4': [],
    'Q5': [],
    'Deficient': []
}

for element in out:
    visit_number = element[0]
    response = element[1]
    values = (re.sub("[\[\]]", "", response)).split(",")
    
    columns['ID'].append(visit_number)
    columns['Q1'].append(values[0])
    columns['Q2'].append(values[1])
    columns['Q3'].append(values[2])
    columns['Q4'].append(values[3])
    columns['Q5'].append(values[3])
    columns['Deficient'].append(values[4])

df = pd.DataFrame(columns)

df['Q3'].value_counts()

def def_column(df):
    new_column = []

    for _, row in df.iterrows():
        if row['Q1'] == 'No' or row['Q2'] == ' No':
            new_column.append('non deficient')
        elif row['Q3'] == ' Yes' and row['Q4'] == ' Yes' and row['Q5'] == ' Yes':
            new_column.append('non deficient')
        else:
            new_column.append('deficient')

    df['pred_deficient'] = new_column
    return df

result_df = def_column(df)

result_df['pred_deficient'].value_counts()

df_fin = result_df.merge(df_cerumen, on = 'ID', how = 'inner')

df_fin.shape

df_fin[(df_fin['pred_deficient'] == 'deficient') & (df_fin['CDI Flagged Type4'] == 'cerumen deficient')].shape


df_fin[(df_fin['pred_deficient'] == 'non deficient') & (df_fin['CDI Flagged Type4'] == 'cerumen deficient')]
