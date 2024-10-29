import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import telegram
from datetime import datetime

h2_text, sub_links = [], []
project_name, project_description, project_duration, project_budget, project_offers,average_offers = [], [], [], [], [],[]

# Projects at least 24 hour
for num in range(0, 10):
    sub_links.clear()  # Clear sub_links for each page to avoid duplicates
    main_url = f'https://mostaql.com/projects?page={num}&budget_max=10000&sort=latest'
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    
    main_response = requests.get(url=main_url, headers=headers)
    main_soup = BeautifulSoup(main_response.content, 'html.parser')
    
    h2_content = main_soup.find_all("h2", {"class": "mrg--bt-reset"})
    for h2 in h2_content:
        h2_text.append(h2.text.strip())
        sub_links.append(h2.a['href'])

    for link in sub_links:
        sub_response = requests.get(url=link, headers=headers).content
        sub_soup = BeautifulSoup(sub_response, 'html.parser')

        # اسم المشروع
        h1_content = sub_soup.find('h1')
        project_name.append(h1_content.text.strip() if h1_content else 'N/A')
        
        # وصف المشروع
        description = sub_soup.select_one("#project-brief-panel")
        project_description.append(description.text.replace('\n', '').strip() if description else 'N/A')
        
        # ميزانية المشروع
        budget = sub_soup.select_one("div.hidden-sm > div:nth-child(2) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)")
        project_budget.append(budget.text.replace('\n', '').strip() if budget else 'N/A')
        
        # مدة تنفيذ المشروع
        duration = sub_soup.select_one("div.hidden-sm > div:nth-child(2) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(4) > td:nth-child(2)")
        project_duration.append(duration.text.replace('\n', '').strip() if duration else 'N/A')
        
        # عدد العروض المقدمة لهذا المشروع
        offers = sub_soup.select_one("div.hidden-sm > div:nth-child(2) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(6) > td:nth-child(2)")
        project_offers.append(offers.text.replace('\n', '').strip() if offers else 'N/A')
        # متوسط سعر العروض المقدمة لهذا المشروع
        average = sub_soup.select_one("#project-meta-panel > div:nth-child(1) > table > tbody > tr:nth-child(5) > td:nth-child(2) > span")
        average_offers.append(average.text.replace('\n','').strip())
        # Adding delay to avoid getting blocked
        time.sleep(1)

#حفظ البيانات في ملف اكسيل باستخدام "pandas"
excel_file = f'Mostaql_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
data = {
    'اسم المشروع':project_name,
    'وصف المشروع':project_description,
    'ميزانية المشروع':project_budget,
    'مدة المشروع':project_duration,
    'عدد العروض':project_offers,
    'متوسط سعر العروض':average_offers
}
df = pd.DataFrame(data)
df.to_excel(excel_file, index=False)

# Initialize Telegram bot
bot = telegram.Bot(token='8072119179:AAElnuacjR4Hn_Dd6VbvJUYkA-cRsHl9xz4')

# Send Excel file to Telegram
with open(excel_file, 'rb') as f:
    bot.send_document(chat_id='7030076829', document=f, caption='Mostaql Projects')

# Delete the Excel file
os.remove(excel_file)
