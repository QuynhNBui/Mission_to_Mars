from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
import pymongo
import scrape_mars

app = Flask(__name__)

#Set up mongo connection
conn = 'mongodb://localhost:27017'

client = pymongo.MongoClient(conn)
db = client.mars_db
db.mars_facts.drop()
collection = db.mars_facts

@app.route("/")
def home():
    mars = list(db.mars_facts.find())
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
    mars = scrape_mars.scrape()
    print('\n')
    db.mars_facts.update({}, mars, upsert = True)
    return redirect("/", code = 302)

if __name__ =="__main__":
    app.run(debug=True)