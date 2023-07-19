from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import pymongo

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            search_input = request.form['content']
            c=search_input.split()
            d=''
            for i in c:
                d+=i+'+'
            flipcart_url='https://www.flipkart.com/search?q='+d
            big_box=urlopen(flipcart_url)
            big_box_readble=big_box.read()
            big_box_html=bs(big_box_readble,'html.parser')
            prd_box=big_box_html.find_all('div',{'class':'_1AtVbE col-12-12'})
            prd_link='https://www.flipkart.com'+prd_box[2].div.div.div.a['href']
            prd_page=urlopen(prd_link)
            prd_page_readble=prd_page.read()
            prd_page_html=bs(prd_page_readble,'html.parser')
            prd_review_box=prd_page_html.find('div',{'class':'col JOpGWq'})
            all_link_in_review_box=prd_review_box.find_all('a')
            reviewall_link=all_link_in_review_box[-1]
            reviewall_url=reviewall_link['href']
            x,y=1,1
            rattings,names,reviews_,img,detailed_reviews,output=[],[],[],[],[],[]
            mydict={}
            while True:
                reviewall_link_bypage='https://www.flipkart.com'+reviewall_url+'&page='+str(x)
                reviewall_page=urlopen(reviewall_link_bypage)
                reviewall_page_readble=reviewall_page.read()
                reviewall_page_html=bs(reviewall_page_readble,'html.parser')
                right_box=reviewall_page_html.find('div',{'class':'_1YokD2 _3Mn1Gg col-9-12'})
                all_review_section=right_box.find_all('div',{'class':'_1AtVbE col-12-12'})
                z=len(all_review_section)
                if x==1:
                    last_page=all_review_section[z-1].div.span.text
                    a=len(last_page)
                    last_page_no=last_page[10:a]
                    n=''
                    for i in last_page_no:
                        if i==',':
                            continue
                        n+=i
                    
                if x==int(n):
                    break
                for j in range(2,z-1):
                    try:
                        rattings=all_review_section[j].div.div.div.text[0]
                    except Exceptionn as e:
                        print('No ratting found')
                    try:
                        reviews_=all_review_section[j].div.div.div.p.text
                    except Exceptionn as e:
                        print('No Comment head found')
                    try:
                        names=all_review_section[j].div.div.find('div',{'class':'row _3n8db9'}).p.text
                    except Exceptionn as e:
                        print('No name found')
                    try:
                        detailed_reviews=all_review_section[j].div.div.find('div',{'class':'t-ZTKy'}).div.div.text
                    except Exceptionn as e:
                        print('No review found')
                    mydict={'No':y,'Product':search_input,'Name':names,'Ratting':rattings,'Review':reviews_,'Detailed Review':detailed_reviews}
                    output.append(mydict)
                    y+=1
                x+=1

            from pymongo.mongo_client import MongoClient
            uri = "mongodb+srv://asutoshp10:pradhan1004@cluster0.8p1kioe.mongodb.net/?retryWrites=true&w=majority"
            client = MongoClient(uri)
            try:
                client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                print(e)
            db=client["flipcart_Webscrapper"]
            coll=db[f"{search_input} scrap"]
            coll.insert_many(output)

            return render_template('result.html', reviews=output[0:(len(output)-1)])
        except Exception as e:
            logging.info(e)
            return 'No review found'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
