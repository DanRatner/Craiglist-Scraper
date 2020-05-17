import os
import time
import requests
import smtplib
import numpy as np
from bs4 import BeautifulSoup
from flask_mail import Mail, Message
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
#--------end imports-------------

# Flask config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465

app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


#Global Variables
url = ""
email_chosen = ""
toggled= False




"""
URL Creator
Takes data parsed from form, creates a URL with data
Needs to know if car, part, or other
May add more details
Returns URL- used as global variable for other functions
"""
def create_url(location, postal, max_price, radius, query, carorpart):
    #Check if car or part
    if carorpart == "car":
        url = f"https://{location}.craigslist.org/search/cto?sort=date&cmax_price={max_price}&postal={postal}&query={query}&search_distance={radius}&srchType=T"
    elif carorpart == "part":
        url = f"https://{location}.craigslist.org/search/pts?query={query}&sort=date&search_distance={radius}&postal={postal}&max_price={max_price}"
    else:
        url = "https://{location}.craigslist.org/search/sss?query={query}&sort=date&search_distance={radius}&postal={postal}&max_price={max_price}"
    return url



#Send Mail Function
def sendEmail(title, url):
    title1 = list(title)
    url1 = url
    print(title1, url1)
    listings = ""
    for item in range(len(title1)):
        listings += "Listing: " + str(item + 1) + "\nTitle: " + title1[item]+ "\nURL: " + url1[item] + "\n\n"

    msg = Message('New Craiglist Listings!', sender = 'newcraiglistlistings@gmail.com', recipients = [email_chosen])
    msg.body = listings
    mail.send(msg)

    print("email sent")


"""
Web Scraper
Finds out how many pages, scans all pages.
Returns 2 lists- titles and urls
May add prices later
"""
def scrape():
    #Variables
    titles_list = []
    url_list = []
    iterations = 0
    pages = 0

    #Find the number of pages
    response = requests.get(url)

    data = response.text

    soup = BeautifulSoup(data, 'lxml')

    results_num = soup.find('div', class_= 'search-legend')

    #Find out how many total items
    results_total = int(results_num.find('span', class_='totalcount').text)

    #Calculate how many pages to scan throught
    pages = np.arange(0, results_total+1, 120)


    #scrape each page
    for page in pages:

        #get request
        response = requests.get(url + "s=" + str(page))
        data = response.text

        #Define what will be scraped
        soup = BeautifulSoup(data, 'lxml')


        #Remove all the non ascii characters (so mail doesn't mess up)
        def _removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

        #Scrape all titles
        for title in soup.findAll('a', {'class': 'result-title'}):
            item = (_removeNonAscii(title.text))
            titles_list.append(item.strip())

        #Scrape links to titles
        for link in soup.findAll("a", {"class": "result-title hdrlnk"}):
            url_list.append(link["href"])

        iterations += 1

        # print("Page " + str(iterations) + " scraped successfully!")

    #Return info
    return titles_list, url_list

#Find the difference between two lists
def list_difference(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif







#Routes...
@app.route('/', methods=['GET', 'POST'])
def index():
    #Parse information
    if request.method == 'GET':
        #Render template with new info...
        return render_template('index.html', email=session.get('email', ''), location=session.get('location', ''),postal=session.get('postal', ''), max_price=session.get('max_price', ''), radius=session.get('radius', ''), query=session.get('query', ''))

    #Pass information to CL
    email = request.form['email']
    location = request.form["location"]
    postal = request.form["postal"]
    max_price = request.form["max_price"]
    radius = request.form["radius"]
    query = request.form["query"]
    carorpart = request.form["carorpart"]
    session['email'] = email
    session['location'] = location
    session['postal'] = postal
    session['max_price'] = max_price
    session['radius'] = radius
    session['query'] = query
    session['carorpart'] = carorpart


    global url, toggled, email_chosen


    if toggled == True:
            #Get a baseline for current titles/urls
        current_titles = scrape()[0]
        current_urls = scrape()[1]

        #Wait before each scan (may make this an option for users)
        time.sleep(10)

        print("completing a test")

        #Scan for any new titles or URLS
        new_titles = scrape()[0]
        new_urls = scrape()[1]

        #Check if there are any new titles
        if current_titles[0] != new_titles[0]:

            print("New listings!")

            #Subtract old url/title list from new one
            #May cause issues if posting was deleted... of well for now
            updated_titles = set(new_titles) - set(current_titles)
            updated_urls = list_difference(new_urls, current_urls)

            #Send out the email
            sendEmail(updated_titles,updated_urls)

            #Create new baseline
            current_titles = scrape()[0]
            current_urls = scrape()[1]

    #Submit Information
    if request.form['submit'] == 'Update Info':
        #Set info
       
        email_chosen = email
        url = create_url(location, postal, max_price, radius, query, carorpart)
        flash('Info set')
        toggled = False

    #Start scraping
    elif request.form['submit'] == 'Start Scraping':
        if url == "":
            flash('Make sure you enter in your info!')
        else:
            toggled = True
            

    #Stop scraping
    elif request.form['submit'] == 'Stop Scraping':
        toggled = False

    

    #Redirect
    return redirect(url_for('index'))



#Run Application
if __name__ == '__main__':
    app.run()








