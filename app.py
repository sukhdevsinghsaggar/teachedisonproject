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
import http.client
from functools import wraps
import plotly.plotly as py
import plotly.graph_objs as go
import http.client
import json
import thread
import requests
from database_setup import Base,Mails

app = Flask(__name__, static_folder="static")

engine = create_engine('sqlite:///sentmails.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getsub():
    conn = http.client.HTTPSConnection("api.sendgrid.com")
    payload = "{}"
    headers = { 'authorization': "Bearer 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" }
    conn.request("GET", "/v3/contactdb/recipients", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    count = data['recipient_count']
    content = data['recipients']
    email = ""
    for x in range (count - 1):
      email += "{\"email\":\"" + content[x]['email'] + "\"},"
    email += "{\"email\":\"" + content[count - 1]['email'] + "\"}"
    return email

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
        conn = http.client.HTTPSConnection("api.sendgrid.com")
        payload = "{\"personalizations\":[{\"to\":[ "+ getsub() +" ],\"subject\":\" " + subject + " \"}],\"from\":{\"email\":\"sukhdev3534@gmail.com\",\"name\":\"Sukhdev Singh\"},\"reply_to\":{\"email\":\"sukhdev3534@gmail.com\",\"name\":\"Sukhdev Singh\"},\"subject\":\" " + subject + "\",\"content\":[{\"type\":\"text/html\",\"value\":\"<html><p>" + content + "</p></html>\"}]}"
        headers = {
            'authorization': "Bearer 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",
            'content-type': "application/json"
        }
        conn.request("POST", "/v3/mail/send", payload, headers)
        res = conn.getresponse()
        data = res.read()
        newItem = Mails(subject=subject, body=content)
        session.add(newItem)
        session.commit()
        return render_template('send.html')
    else:
        return render_template('send.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8020)
