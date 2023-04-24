import requests
from bs4 import BeautifulSoup
import lxml


# load first floorsheet page 
def load_floorsheet():
    floorsheet =  requests.get('https://merolagani.com/Floorsheet.aspx')
    session_cookie = floorsheet.headers['Set-Cookie'].split()[0]
    soup = BeautifulSoup(floorsheet.text,"lxml")

    headers = {
        'cookie': session_cookie,
        'origin': 'https://merolagani.com',
        'referer': 'https://merolagani.com/Floorsheet.aspx',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',    
    }
    
    return soup, headers

soup, headers = load_floorsheet()
month = '1'
year = '2015'
day = '1'
pages = 1
f = open('floorsheet.txt', 'w') # enter file location

for year in range(2015,2023):
    for month in range(1,13):
        for day in range(1,33):
            print('day = ' + str(day) )
            pages = 1
            while 1:
                page = str(pages)
                try:
                    payload={
                        '__EVENTTARGET':'' ,
                        '__EVENTARGUMENT': '',
                        '__VIEWSTATE': soup.find(id="__VIEWSTATE").get("value"),
                        '__VIEWSTATEGENERATOR':  soup.find(id="__VIEWSTATEGENERATOR").get("value"),
                        '__EVENTVALIDATION': soup.find(id="__EVENTVALIDATION").get("value"),
                        'ctl00$ASCompany$hdnAutoSuggest': soup.find(id="ctl00_ASCompany_hdnAutoSuggest").get("value"),
                        'ctl00$ASCompany$txtAutoSuggest': soup.find(id="ctl00_ASCompany_txtAutoSuggest").get("value"),
                        'ctl00$txtNews': soup.find(id="ctl00_txtNews").get("value"),
                        'ctl00$AutoSuggest1$hdnAutoSuggest': soup.find(id="ctl00_AutoSuggest1_hdnAutoSuggest").get("value"),
                        'ctl00$AutoSuggest1$txtAutoSuggest': soup.find(id="ctl00_AutoSuggest1_txtAutoSuggest").get("value"),
                        'ctl00$ContentPlaceHolder1$ASCompanyFilter$hdnAutoSuggest': soup.find(id="ctl00_ContentPlaceHolder1_ASCompanyFilter_hdnAutoSuggest").get("value"),
                        'ctl00$ContentPlaceHolder1$ASCompanyFilter$txtAutoSuggest': soup.find(id="ctl00_ContentPlaceHolder1_ASCompanyFilter_txtAutoSuggest").get("value"),
                        'ctl00$ContentPlaceHolder1$txtBuyerBrokerCodeFilter': soup.find(id="ctl00_ContentPlaceHolder1_txtBuyerBrokerCodeFilter").get("value"),
                        'ctl00$ContentPlaceHolder1$txtSellerBrokerCodeFilter': soup.find(id="ctl00_ContentPlaceHolder1_txtSellerBrokerCodeFilter").get("value"),
                        'ctl00$ContentPlaceHolder1$txtFloorsheetDateFilter': str(month) + '/' + str(day) + '/' + str(year),
                        'ctl00$ContentPlaceHolder1$PagerControl1$hdnPCID': soup.find(id="ctl00_ContentPlaceHolder1_PagerControl1_hdnPCID").get("value"),
                        'ctl00$ContentPlaceHolder1$PagerControl1$hdnCurrentPage':page, 
                        'ctl00$ContentPlaceHolder1$PagerControl1$btnPaging': soup.find(id="ctl00_ContentPlaceHolder1_PagerControl1_btnPaging").get("value"),
                        'ctl00$ContentPlaceHolder1$PagerControl2$hdnPCID':  soup.find(id="ctl00_ContentPlaceHolder1_PagerControl2_hdnPCID").get("value"),
                        'ctl00$ContentPlaceHolder1$PagerControl2$hdnCurrentPage': soup.find(id="ctl00_ContentPlaceHolder1_PagerControl2_hdnCurrentPage").get("value"),
                        }
                    
                    floorsheet_test=requests.post("https://merolagani.com/floorsheet.aspx", headers= headers , data=payload)
                    soup = BeautifulSoup(floorsheet_test.text,"lxml")
                    list = soup.find_all('td',class_=lambda classes:'td-icon' not in classes)
                    counter = 0
                    pages = pages +1
                    for i in list:
                        print(i.text.strip(), end="\t")
                        f.write(i.text.strip() + "\t")
                        counter = counter + 1
                        if counter==8:
                            print("\n",end='')
                            counter=0
                            f.write("\n")
                except AttributeError:
                    pages = 1
                    page = str(pages)
                    soup, headers = load_floorsheet()
                    break
                
                
                





