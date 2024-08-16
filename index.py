from flask import Flask,redirect,render_template,url_for,request,flash,session
import mysql.connector

import os
from werkzeug.utils import secure_filename


db = mysql.connector.connect(#Defining the connection with our data base

    host = "127.0.0.1",
    port = "3306",
    user = "abd",
    password = "1234567",
    database = "UpbNotes")

cursor = db.cursor()#used to execute commands on our database 

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)#Our flask web application instance
app.secret_key = "upbnotes"#Secret key necessary for flash messaging

uploadDirectory = os.path.join(APP_ROOT, 'static')

ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = uploadDirectory

def deleteFile(filename):

    if filename:

        os.remove(os.path.join(app.config["UPLOAD_FOLDER"],filename))


def allowed_file(filename):

    cursor.execute(f"SELECT file FROM Notes WHERE file = '{filename}';")
    search = cursor.fetchone()

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and \
           not search

@app.route('/', methods = ["POST", "GET"])
def home():

    if request.method == "POST":

        searchResult = session["searchResult"]
        search = session["search"]
        numOfRes = session["numOfRes"]

        numOfRes = session["numOfRes"]

        sub = ""
        filSel = ""

        if request.form.get("searchFilter") == "Subject Name":
            sub = "selected"

        elif request.form.get("searchFilter") == "File Name":
            filSel = "selected"

        if "searchNotes" in request.form:
        
            search = request.form.get("searchNotes")
            op = request.form.get("searchFilter")
            session["search"] = search
            flash("Upload A New Note:","message")

            if op == "Subject Name":# Search by subject name

                cursor.execute(f"SELECT * FROM Notes WHERE subject LIKE '%{search}%';")
                result = cursor.fetchall()
                numOfRes = len(result)
                session["searchResult"] = result
                session["numOfRes"] = len(result)

                flash(f"{numOfRes} Results For Subject '{search}':",'info')
                return render_template("home.html",ID = "Auto_Assigned",subjectSelect = "selected" , NoteResults = result , opName = "uploadNote", opValue = "Upload New Note")

            elif op == "File Name":# Search by file name

                cursor.execute(f"SELECT * FROM Notes WHERE file LIKE '%{search}%';")
                result = cursor.fetchall()
                numOfRes = len(result)
                session["searchResult"] = result
                session["numOfRes"] = len(result)


                flash(f"{numOfRes} Results For File '{search}':",'info')
                return render_template("home.html", ID = "Auto_Assigned",fileSelect = "selected" , NoteResults = result, opName = "uploadNote", opValue = "Upload New Note")

            else:#No filters

                cursor.execute(f"SELECT * FROM Notes WHERE subject LIKE '%{search}%' || file LIKE '%{search}%';")
                result = cursor.fetchall()
                numOfRes = len(result)
                session["searchResult"] = result
                session["numOfRes"] = len(result)

                flash(f"{numOfRes} Results For '{search}':",'info')
                return render_template("home.html", ID = "Auto_Assigned", NoteResults = result, opName = "uploadNote", opValue = "Upload New Note")

        elif "deleteNote" in request.form:
        
            id = request.form.get("noteID")

            cursor.execute(f"SELECT file FROM Notes WHERE id = {id};")
            filename = cursor.fetchone()[0]

            cursor.execute(f"DELETE FROM Notes WHERE id = {id};")
            db.commit()

            deleteFile(filename)

            lastIndex = cursor.lastrowid 

            if lastIndex <= 1:
                lastIndex = 2
              
            cursor.execute(f"ALTER TABLE Notes AUTO_INCREMENT = {lastIndex - 1};")
            
            if request.form.get("searchFilter") == "Subject Name":

                cursor.execute(f"SELECT * FROM Notes WHERE subject LIKE '%{search}%';")
                searchResult = cursor.fetchall()

                numOfRes = len(searchResult)
                session["numOfRes"] = numOfRes
                session["searchResult"] = searchResult

                sub = "selected"
                flash(f"{numOfRes} Results For Subject '{search}'","info")
                

            elif request.form.get("searchFilter") == "File Name":

                cursor.execute(f"SELECT * FROM Notes WHERE file LIKE '%{search}%';")
                searchResult = cursor.fetchall()

                numOfRes = len(searchResult)
                session["numOfRes"] = numOfRes
                session["searchResult"] = searchResult

                filSel = "selected"
                flash(f"{numOfRes} Results For File '{search}'","info")                
            else:

                cursor.execute(f"SELECT * FROM Notes WHERE file LIKE '%{search}%' || subject LIKE '%{search}%';")
                searchResult = cursor.fetchall()

                numOfRes = len(searchResult)
                session["numOfRes"] = numOfRes
                session["searchResult"] = searchResult

                flash(f"{numOfRes} Results for '{search}'","info")
            

            flash(f"Successfully Deleted Note Number: {id}", 'warning')
            flash("Upload A New Note","message")
            return render_template("home.html", ID = "Auto_Assigned", subjectSelect = sub, fileSelect = filSel,NoteResults = searchResult, opName = "uploadNote", opValue = "Upload New Note")

        elif "uploadNote" in request.form:

            subject = request.form.get("subjectName")
            text = request.form.get("writtenNote")
            file = request.files.get("noteFile")

            if subject == "":

                flash("ERROR: INVALID SUBJECT NAME!", "error")
                return render_template("home.html", ID = "Auto_Assigned", NoteResults = searchResult, opName = "uploadNote", opValue = "Upload New Note")
            if text == "":
                flash("ERROR: NO WRITTEN NOTE PROVIDED!","error")
                return render_template("home.html", ID = "Auto_Assigned", NoteResults = searchResult, opName = "uploadNote", opValue = "Upload New Note")

            if len(file.filename) > 1000:#Filename is too long

                flash("ERROR: FILE NAME TOO LONG!","error")
                return render_template("home.html", ID = "Auto_Assigned", NoteResults = searchResult, opName = "uploadNote", opValue = "Upload New Note")

            
            cursor.execute(f"INSERT INTO Notes(subject, note, file) VALUES('{subject}','{text}','');")
            db.commit()
            lastID = cursor.lastrowid
            cursor.execute(f"SELECT * FROM Notes WHERE id = {lastID};")

            searchResult = cursor.fetchall()
            search = searchResult[0][1]
            session["searchResult"] = searchResult
            session["search"] = search
            session["numOfRes"] = 1

            if not file or not allowed_file(file.filename):#File not inserted or extension invalid.
                
                flash(f"Successfully Added Note, But No File Was Attached.:","info")
                return render_template("home.html", ID = "Auto_Assigned", NoteResults = searchResult, opName = "uploadNote", opValue = "Upload New Note")
            
            filename = secure_filename(file.filename)

            cursor.execute(f"UPDATE Notes SET file = '{filename}' WHERE id = {lastID};")
            db.commit()

            file.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))

            cursor.execute(f"SELECT * FROM Notes WHERE id = {lastID};")
            searchResult = cursor.fetchall()
            search = searchResult[0][1]
            session["searchResult"] = searchResult
            session["search"] = search
            session["numOfRes"] = 1
                
            flash(f"Successfully Added Note:","info")
            return render_template("home.html", ID = "Auto_Assigned", NoteResults = searchResult, opName = "uploadNote", opValue = "Upload New Note")

        elif "editNoteList" in request.form:

            id = request.form.get("noteID")

            flash(f"Edit Note Number {id}:","message")
            flash(f"{numOfRes} Results For File '{search}'","info")  
            return render_template("home.html",ID = id ,subjectSelect = sub, fileSelect = filSel,NoteResults = searchResult, opName = "editNote", opValue = f"Save Changes")

        elif "editNote" in request.form:

            changed = False

            subject = request.form.get("subjectName")
            text = request.form.get("writtenNote")
            noteFile = request.files.get("noteFile")
            id = request.form.get("noteID")

            if noteFile.filename and allowed_file(noteFile.filename):

                changed = True
                filename = secure_filename(noteFile.filename)

                cursor.execute(f"SELECT file FROM Notes WHERE id = {id};")
                oldFilename = cursor.fetchone()[0]

                cursor.execute(f"UPDATE Notes SET file = '{filename}' WHERE id = {id};")
                db.commit()

                deleteFile(oldFilename)
                noteFile.save(os.path.join(app.config["UPLOAD_FOLDER"],filename))

            if subject != "":

                changed = True
                cursor.execute(f"UPDATE Notes SET subject = '{subject}' WHERE id = {id};")
                db.commit()

            if text != "":

                changed = True
                cursor.execute(f"UPDATE Notes SET note = '{text}' WHERE id = {id};")
                db.commit()
            
            if changed:

                cursor.execute(f"SELECT * FROM Notes WHERE id = {id};")
                note = cursor.fetchall()
                flash(f"Successfully Saved Changes For Note Number {id}:","info")
                session["searchResult"] = note
                session["numOfRes"] = 1
                session["search"] = ""
                searchResult = session["searchResult"]
            else:

                flash(f"No Changes Made To Note Number {id}:","info")

            return render_template("home.html", ID = "Auto_Assigned",subjectSelect = sub, fileSelect = filSel,NoteResults = searchResult, opName = "uploadNote", opValue = f"Upload New Note")
    #GET METHOD   
    session["numOfRes"] = 0
    session["search"] = ""
    session["searchResult"] = []
    session["currentNote"] = []
    flash("No Results.","info")
    flash("Upload A New Note:","message")
    return render_template("home.html",opName= "uploadNote",opValue = "Upload New Note")

if __name__ == "__main__" :#Running the web application
    app.run()