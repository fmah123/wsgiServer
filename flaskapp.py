from flask import Flask, render_template

app = Flask(__name__) 
#line 3: __name__ means current file, in this case main.py, current file will represent my web app.
@app.route("/")
# will represent the site that will be developed like https://www.google.com/, that what line 5 does.
#When the users go to the page www.examplePage.com/ then function home() will activate
def home(): 
    return render_template("home.html") #render_template() is from flask framework, looks for a temple html file.

@app.route("/about")
def about(): 
    return render_template("about.html")


@app.route("/anotherPage")
def anotherPage():
    return render_template("anotherPage.html")    

app =wsgi.app
    
     
    
