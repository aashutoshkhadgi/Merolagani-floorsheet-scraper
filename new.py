import requests
from bs4 import BeautifulSoup
import lxml
import json
from datetime import date
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError, Timeout, RequestException
import threading
import time
import logging
import click


#load floorsheet page





@click.command()
@click.option("--start_date",prompt="Enter the start date to scrape teh floorsheet in AD (yyyy-mm-dd)",help="start date to scrape teh floorsheet in AD (yyyy-mm-dd)")
@click.option("--end_date",default=None,help="end date to scrape teh floorsheet in AD (yyyy-mm-dd)")
@click.option("--debug", is_flag=True, help="Turn on debug mode")
def main(start_date,end_date,debug):
    """
        Scrapes the meralaganin floorsheet and returns that data is json format
    """

    print(start_date)
    print(end_date)




if __name__=='__main__':
    main()