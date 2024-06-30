import requests
from bs4 import BeautifulSoup
import lxml
import json
from datetime import datetime, timedelta, date
from requests.exceptions import (
    ReadTimeout,
    ConnectTimeout,
    HTTPError,
    Timeout,
    RequestException,
)
import threading
import time
import logging
import click
import os
import fcntl

lock = threading.Lock()




class NoDataException(Exception):
    "Raised when there is no data"
    pass


# load floorsheet page
def load_floorsheet():
    try:
        floorsheet = requests.get("https://merolagani.com/Floorsheet.aspx")
        session_cookie = floorsheet.headers["Set-Cookie"].split()[0]
        soup = BeautifulSoup(floorsheet.text, "lxml")
        headers = {
            "cookie": session_cookie,
            "origin": "https://merolagani.com",
            "referer": "https://merolagani.com/Floorsheet.aspx",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded",
        }
    except requests.exceptions.ReadTimeout:
        print("Read timeout exception in load  stage")

        soup, headers = load_floorsheet()
    except:
        soup, headers = load_floorsheet()

    return soup, headers


def extract_day_month(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Extract the day and month
    day = date_obj.day
    month = date_obj.month
    year = date_obj.year

    return day, month, year


def loop_through_days_between_dates(start_date, end_date):
    date = set()
    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Iterate through each day between start_date and end_date
    current_date = start_date
    while current_date <= end_date:
        print(current_date.strftime("%Y-%m-%d"))
        date.add(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return date


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


def load_data(headers,data):
    try:
        floorsheet = requests.post("https://merolagani.com/floorsheet.aspx", headers= headers , data=data)
        soup = BeautifulSoup(floorsheet.text,"lxml")
        list = soup.find_all('td',class_=lambda classes:'td-icon' not in classes)
    except requests.exceptions.ReadTimeout:
        print("Read timeout exception in extract stage")
        soup, list = load_data(headers,data)
    except:
        soup, list = load_data(headers,data)
    return soup, list



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


def extract_data(list):
    try:
        temp = []
        keys = ["no","transaction_id", "symbol","buyer","seller","rate","quantity","amount","date"]
        data = {key: None for key in keys}
        for i in range(0,len(list),8):
            # if counter==8:
            #     print("\n",end='')
            #     counter=0
            data["no"] = int(list[i].text.strip())
            data["transaction_id"] = str(list[i+1].text.strip())
            data["symbol"] = str(list[i+2].text.strip())
            data["buyer"] = str(list[i+3].text.strip())
            data["seller"] = str(list[i+4].text.strip())
            data["quantity"] = int(list[i+5].text.strip().replace(',', ''))
            data["rate"] = float(list[i+6].text.strip().replace(',', ''))
            data["amount"] = float(list[i+7].text.strip().replace(',', ''))
            data["date"] = add_date(data["transaction_id"])
            temp.append(json.dumps(data))
            # print(data)
    # except ValueError:
    #     print("error in value")
    #     extract_data(list)
    except AttributeError:
        print("triggered Attribute error")
    except IndexError:
        print("triggered index error")
    return temp

def write_to_file(data,date):
    with lock:
        with open("floorsheet/floorsheet-" + str(date) + ".json", 'a') as f:
            for item in data:
                f.write(item + "\n")


def execute(date,soup,headers,page):
    try:
        print(f"loading floorsheet page {page} of {date}")
        day, month, year = extract_day_month(date)
        payload = generate_payloads(soup, year, month, day, page)
        soup, list = load_data(headers,payload)
        value = extract_data(list)
        if not value:
            raise NoDataException("e")
        write_to_file(value,date)     

    except NoDataException:
        print("no data exception")       
        threading.current_thread().exception = "e"

    


def initialize(date):
    soup, headers = load_floorsheet()
    day, month, year = extract_day_month(date)
    payload = generate_payloads(soup, year, month, day, page = 1)
    #check if data is available in the above date
    soup, list = load_data(headers, payload)
    try:
        if not list:
            raise NoDataException("e")
            print(f"No data for date {date}")
            return(5)
        else:
            print(f"Data available for the date {date}")
            print("Checking bumber of pages")
            last_page = int(soup.find('a', {'title': 'Last Page'}).get('onclick').split('"')[1])
            print(f"found {last_page} number of pages")
            # no_of_threads = int(os.cpu_count())
            no_of_threads = last_page
            page = 1
            flag = 0
            while page <= last_page:      
                threads = []
                try:                    
                    for i in range(no_of_threads):
                        t=threading.Thread(target=execute,args=(date,soup,headers,page+i))
                        threads.append(t)
                    
                    for i in threads:
                        i.start()

                    for i in threads:
                        i.join()

                    for i in threads:
                        if hasattr(i,"exception"):
                            flag = 1
                    if flag == 1:
                        break
                except NoDataException:
                    print(f"No data found on thread")
                page = page + no_of_threads
    except NoDataException:
        print(f"No data found on date {date}")



@click.command()
@click.option(
    "--start_date",
    prompt="Enter the start date to scrape teh floorsheet in AD (yyyy-mm-dd)",
    help="start date to scrape teh floorsheet in AD (yyyy-mm-dd)",
)
@click.option(
    "--end_date",
    default=None,
    help="end date to scrape teh floorsheet in AD (yyyy-mm-dd)",
)
@click.option("--debug", is_flag=True, help="Turn on debug mode")
def main(start_date, end_date, debug):
    """
    Scrapes the merolagani floorsheet and returns that data is json format
    """
    number_of_threads = int(os.cpu_count())
    date_list = set()
    date_list.add(start_date)
    start_day, start_month, start_year = extract_day_month(start_date)
    if end_date is not None:
        date_list = loop_through_days_between_dates(start_date, end_date)
    date_list = sorted(date_list)
    
    for i in date_list:
        f = open("floorsheet/floorsheet-" + str(i) + ".json", 'w')
        f.close()
        initialize(i)

if __name__ == "__main__":
    main()


