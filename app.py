import sendgrid
import os
from sendgrid.helpers.mail import *
from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from functools import wraps
import http.client
import json
import thread
import requests
from database_setup import Base,Mails
from urlparse import urlparse
from threading import Thread
import httplib, sys
import Queue


app = Flask(__name__, static_folder="static")

engine = create_engine('sqlite:///sentmails.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def getsub():
    conn = httplib.HTTPSConnection("api.sendgrid.com")
    payload = "{}"
    headers = { 'authorization': "Bearer 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" }
    conn.request("GET", "/v3/contactdb/recipients", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    count = data['recipient_count']
    content = data['recipients']
    email = Queue.Queue()
    for x in range(count):
        email.put(content[x]['email'])
    return email
    
      
def send_email(subject, content):
    email = getsub()
    print email
    for mailid in iter(email.get, None):
        conn = httplib.HTTPSConnection("api.sendgrid.com")
        payload = "{\"personalizations\":[{\"to\":[ {\"email\":\""+ mailid +"\"} ],\"subject\":\" " + subject + " \"}],\"from\":{\"email\":\"sukhe013@gmail.com\",\"name\":\"Sukhdev Singh\"},\"reply_to\":{\"email\":\"sukhe013@gmail.com\",\"name\":\"Sukhdev Singh\"},\"subject\":\" " + subject + "\",\"content\":[{\"type\":\"text/html\",\"value\":\"<html><p>" + content + "</p></html>\"}]}"
        headers = {
            'authorization': "Bearer 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",
            'content-type': "application/json"
        }
        conn.request("POST", "/v3/mail/send", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))

@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template('base.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dash_home.html')

@app.route('/dashboard/subscribers', methods=['GET', 'POST'])
def subscribers():
    return render_template('subscribers.html')

@app.route('/dashboard/csv', methods=['GET', 'POST'])
def csv():
    return render_template('csv.html')
  
@app.route('/dashboard/sent', methods=['GET', 'POST'])
def sent():
    mail = session.query(Mails).all()
    return render_template('sent.html', mail = mail)

@app.route('/dashboard/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        subject = request.form['subject']
        content = request.form['Message']
        thread.start_new_thread(send_email, (subject, content))
        newItem = Mails(subject=subject, body=content)
        session.add(newItem) 
        session.commit()
        return render_template('send.html', msg="Your email will be delivered to the subscribers in the background!")
    else:
        return render_template('send.html', msg="")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8020)
