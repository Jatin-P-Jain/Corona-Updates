import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import requests
import re
from datetime import date
from datetime import datetime
from datetime import timedelta
from twilio.rest import Client 

def scrape_values():
    def format_no(num_str):
        num_str=list(num_str)
        num_str[:] = (value for value in num_str if value != ',')
        num_str=''.join(num_str)
        return (int(num_str))
    def format_date(date_str):
        date_obj=datetime.strptime(date_str,"%Y-%m-%d")
        date_value=date_obj.strftime("%d/%b/%y")
        return date_value

    page = requests.get("https://www.worldometers.info/coronavirus/country/india/")
    page.content
    stats={}
    Soup=BeautifulSoup(page.content,"html.parser")
    mydivs = Soup.findAll("div", id= "maincounter-wrap")
    for div in mydivs:
        stats[div.find('h1').get_text()]=div.find('div',class_="maincounter-number").get_text().strip()
    divs = Soup.findAll("div", id=lambda x: x and x.startswith('newsdate'))
    today_div=divs[0]
    yesterday_div=divs[1]
    day_before_div=divs[2]
    
    today_date=((today_div.get('id'))[8:])
    today_date=format_date(today_date)
    yesterday_date=((yesterday_div.get('id'))[8:])
    yesterday_date=format_date(yesterday_date)
    day_before_date=((day_before_div.get('id'))[8:])
    day_before_date=format_date(day_before_date)
    
    txt1=today_div.find('ul').get_text()
    txt2=yesterday_div.find('ul').get_text()
    txt3=day_before_div.find('ul').get_text()
    today=re.findall("[\d,]+",txt1)
    yesterday=re.findall("[\d,]+",txt2)
    day_before=re.findall("[\d,]+",txt3)
    corona_values=[]
    for item in stats:
        corona_values.append(stats[item])
    corona_values.append(str(format_no(stats['Coronavirus Cases:'])-(format_no(stats['Recovered:'])+(format_no(stats['Deaths:'])))))
    corona_values.append([today_date,today[0]])
    corona_values.append([yesterday_date,yesterday[0]])
    corona_values.append([day_before_date,day_before[0]])
    corona_values.append(str(round(format_no(stats['Recovered:'])*100/format_no(stats['Coronavirus Cases:']),2)))
    corona_values.append(str(round(format_no(stats['Deaths:'])*100/format_no(stats['Coronavirus Cases:']),2)))
    return corona_values
    
def send_sms(phone):
    account_sid = 'AC41e31dd9772991d1a68e3840b30e158f' 
    auth_token = '8564ee69bf659885cc96569e4af58f91' 
    client = Client(account_sid, auth_token) 
    statistics=scrape_values()
    message = client.messages.create( 
            from_='+12513026259', 
            to=phone,
            body="By Jatin\n\nToday's Corona Update\n\n"+str_total+str_total_recoveries+str_deaths+str_active+"\nNew Cases\n"+str_today_cases+str_yesterday_cases+str_day_before_cases+str_recoveries+str_mortality+"\nHang in There.\nGood Times Loading..."
        ) 
    
statistics=scrape_values()
phones=['+919636245681']
#

#today = date.today()
#yesterday = today - timedelta(days = 1)
#today=today.strftime("%d/%b/%y")
#yesterday=yesterday.strftime("%d/%b/%y")
timestamp=datetime.now().strftime('%I:%M %p')

str_total="Total Cases: "+statistics[0]+"\n"
str_total_recoveries="Total Recoveries: "+statistics[2]+"\n"
str_deaths="Total Deaths: "+statistics[1]+"\n"
str_active="Currently Active: "+statistics[3]+"\n"
str_today_cases=statistics[4][0]+" :  +"+statistics[4][1]+"    -    ("+timestamp+")\n\n"
str_yesterday_cases=statistics[5][0]+" : "+statistics[5][1]+"\n"
str_day_before_cases=statistics[6][0]+" : "+statistics[6][1]+"\n\n"
str_recoveries="Recovery Rate: "+statistics[7]+"%\n"
str_mortality="Mortality Rate: "+statistics[8]+"%\n"

for ph in phones:
    send_sms(ph)