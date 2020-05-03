import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import boto3
import re 
import os

def lambda_handler(event, context):
    
    body = event['Records'][0]['body']
    body = json.loads(body)
    url = body['url']
    product = body['product']
    category = body['category']
    basketurl = os.environ[basketurl]
    
    html = check_inventory(url,basketurl)
    soup = BeautifulSoup(html, 'html.parser')
    selector = soup.find_all('select', class_="js_quantity_dropdown tst_item_count_selection")[0]
    count = int(re.search(r'selected" value="\d+">(\d+)', str(selector)).group(1))
    time_stamp = int(time.time())
    
    result = {
        'product': product,
        'time': time_stamp,
        'count': count
    }
    
    print(result)
    
    # dynamodb = boto3.resource('dynamodb')
    # table = dynamodb.Table('webcrawler_results')
    # table.put_item(Item=result)
    
    data = str.encode(json.dumps(result) + "\n")
    client = boto3.client('firehose')
    response = client.put_record(DeliveryStreamName='webcrawler', Record={'Data': data})
    print(response)
    
    return {
        'statusCode': 200,
        'body': json.dumps('success')
    }


def check_inventory(producturl, basketurl):
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(executable_path='/opt/chromedriver', chrome_options=options)
    browser.get(producturl)
    browser.find_element_by_class_name('js_preventable_buy_action').click()
    time.sleep(0.5)
    browser.get(basketurl)
    browser.find_element_by_id('tst_quantity_dropdown').click()
    browser.find_element_by_xpath('//*[@id="tst_quantity_dropdown"]/option[11]').click()
    browser.find_element_by_xpath('//*[@id="mainContent"]/div[3]/div[1]/div/div[3]/div/div/div[1]/div/form/fieldset/div[2]/div[2]/input').send_keys('500')
    browser.find_element_by_xpath('//*[@id="mainContent"]/div[3]/div[1]/div/div[3]/div/div/div[1]/div/form/fieldset/div[2]/div[2]/div[2]/a').click()
    return browser.page_source