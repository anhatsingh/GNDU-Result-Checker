import requests
from bs4 import BeautifulSoup
import pandas as pd
from difflib import SequenceMatcher
import time


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

df = pd.read_csv("roll_list.csv")


data = {}

start_time = time.time()
for index in df.index:
    print("Getting {}".format(df['roll_no'][index]))
    marks_params = {
                '__VIEWSTATE': '/wEPDwUKMjAwNTM2MjgwMWRkNQzQcB7GPknT/FqDs+wcjM+g+RQWzjcnEH3XkUB9plg=',
                '__VIEWSTATEGENERATOR': 'BD7F1450',
                'ctl00$ContentPlaceHolder1$TXT_StudentID': str(df['Student ID'][index]),
                'ctl00$ContentPlaceHolder1$TXT_StuPassword': str(df['Password'][index]),
                'ctl00$ContentPlaceHolder1$But_StuSignIn': 'Student Sign In'
                }

    marks_params2 = {
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$gridViewStudentHistory',
        '__EVENTARGUMENT': 'Select$0'
        }
    session = requests.session()
    session.post("https://collegeadmissions.gndu.ac.in/loginNew.aspx", data=marks_params)
    evalp = session.post("https://collegeadmissions.gndu.ac.in/reevaluation/ReevaluationApplicationForm.aspx", data=marks_params2)

    soup2 = BeautifulSoup(evalp.text, features="html.parser")

    table = soup2.select("#ContentPlaceHolder1_gridviewsubjectforeev")
    rows = table[0].find_all("tr") if len(table) > 0 else None

    if rows != None:
        for i in range(len(rows) - 1):                
            tds = rows[i+1].find_all("td")
            if len(tds) > 6:
                data[tds[2].getText().strip()] = (tds[3].getText().strip(), tds[5].getText().strip())

print("--- %s seconds ---" % (time.time() - start_time))
df2= pd.DataFrame.from_dict(data)    
df2 = df2.fillna('')

df2.to_csv('temp.csv')