import requests
from bs4 import BeautifulSoup
import lxml
import json
from datetime import date
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, Timeout, RequestException
import threading
import time
class NoDataException(Exception):
    "Raised when there is no data"
    pass


# load first floorsheet page
def load_floorsheet():
    try:
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
    except requests.exceptions.ReadTimeout:
        print("Read timeout exception in load  stage")

        soup, headers = load_floorsheet()
    except:
        soup, headers = load_floorsheet()

    return soup, headers

def add_date(transaction_id):
    try:
        year=int(str(transaction_id)[0:4])
        month=int(str(transaction_id)[4:6])
        day=int(str(transaction_id)[6:8])
        transaction_date = date(year,month,day)
        date_str = transaction_date.strftime('%Y-%m-%d')
        return(date_str)
    except ValueError:
        return("error in date function")

def generate_payloads(soup,year,month,day,page):
    #soup, headers = load_floorsheet()

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

    return payload


def extract_floorsheet(headers, data):
    try:
        floorsheet = requests.post("https://merolagani.com/floorsheet.aspx", headers= headers , data=data)
        soup = BeautifulSoup(floorsheet.text,"lxml")
        list = soup.find_all('td',class_=lambda classes:'td-icon' not in classes)
    except requests.exceptions.ReadTimeout:
        print("Read timeout exception in extract stage")
        soup, list = extract_floorsheet(headers,data)
    except:
        soup, list = extract_floorsheet(headers,data)
    return soup, list


def extract_data(list):
    try:
        temp = []
        for i in range(0,len(list),8):
            # if counter==8:
            #     print("\n",end='')
            #     counter=0
            data["no"] = list[i].text.strip()
            data["transaction_id"] = list[i+1].text.strip()
            data["symbol"] = list[i+2].text.strip()
            data["buyer"] = list[i+3].text.strip()
            data["seller"] = list[i+4].text.strip()
            data["quantity"] = list[i+5].text.strip()
            data["rate"] = list[i+6].text.strip()
            data["amount"] = list[i+7].text.strip()
            data["date"] = add_date(data["transaction_id"])
            temp.append(json.dumps(data))


    except AttributeError:
        print("triggered Attribute error")
    except IndexError:
        print("triggered index error")
    return temp

def write_to_file(f,data):
    for i in data:
        f.write(i+"\n")



def execute(year,month,day,page,soup,headers):
    try:
        print("Fetching records for {0}-{1}-{2} page:{3}".format(year,month,day,page))
        payload = generate_payloads(soup ,year, month,day, page)
        soup, list = extract_floorsheet(headers,payload)
        value =  extract_data(list)
    # #  print(list)
        if not value:
            raise NoDataException("e")
    except NoDataException:
        print("No records found for {0}-{1}-{2} page:{3}".format(year,month,day,page))
        threading.current_thread().exception = "e"

    write_to_file(f,value)
    # breakpoint()




if __name__ =='__main__':
    keys = ["no","transaction_id", "symbol","buyer","seller","rate","quantity","amount","date"]
    data = {key: None for key in keys}
    # soup, headers = load_floorsheet()
    # month = '1'
    # year = '2015'
    # day = '1'
    # pages = 1    f = open('floorsheet.txt', 'w') # enter file location
    month_value = 6
    year_value = 2024
    day_value=2
    threads = 4

    for year in range(year_value,2025):
        for month in range(month_value,13):
            f = open('floorsheet/floorsheet-'+str(year)+'-'+ str(month) +'.txt' , 'w') # enter file location
            for day in range(day_value,33):
                page = 1
                soup, headers = load_floorsheet()
                consecutive_exceptions = 0
                max_consecutive_exceptions = 3

                break_loop = 0
                # execute(year,month,day,page,soup,headers)                print(page)
                while break_loop <= 0:
                    try:
                        threads = []
                        no_of_thread = 4
                        for i in range(no_of_thread):
                            t=threading.Thread(target=execute,args=(year,month,day,page+i,soup,headers))
                            t.daemon = True
                            threads.append(t)

                        for i in threads:
                            i.start()
                            # time.sleep(0.2)

                        for i in threads:
                            i.join()

                        for i in threads:
                            if hasattr(i,"exception"):
                                break_loop = 5
                        # exit(9)
                        # execute(year,month,day,page,soup,headers)
                    except NoDataException as e:
                        print("No records found for {0}-{1}-{2} page:{3}".format(year,month,day,page))
                        print(e)
                        break_loop = 5
                        print("BREAK LOOP " + str(break_loop))
                    except AttributeError as e:
                        print("Attribute error for {0}-{1}-{2} page:{3}".format(year,month,day,page))
                        break_loop += 1
                        print(e)

                    except IndexError as e:
                        print("triggered index error for main")
                        print(e)
                        break_loop += 1

                    page = page + no_of_thread
            exit(9)
            day_value = 1
        month_value = 1

