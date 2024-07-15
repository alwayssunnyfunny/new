from flask import Flask, render_template, request, session, redirect, url_for, flash
import psycopg2
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        dbname='project',
        user='postgres',
        password='admin',
        host='localhost',
        port='5432'
    )

# Validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        semester_id = request.form["semester"]

        # Add user to the database
        add_user(username, email, password, semester_id)
        flash("Account created successfully!")
        return redirect(url_for("loginhello"))

    # Fetch semesters for the dropdown on GET request
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT semester_id, name FROM semester;")
    semesters = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("sign.html", semesters=semesters)

def add_user(username, email, password, semester_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
    
        
        insert_query = '''
            INSERT INTO "user" (username, email, password, semester_id)
            VALUES (%s, %s, %s, %s);
        '''
        
        cursor.execute(insert_query, (username, email, semester_id))
        connection.commit()
        
        print("User added successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    

@app.route("/loginhello", methods=["GET", "POST"])
def loginhello():
    if request.method == "POST":
        email = request.form["email"]
        user = request.form["username"]
        password = request.form["password"]
        semester_id = request.form["semester"]  # This links to sem_id
        
        if is_valid_email(email):
            connection = get_db_connection()
            cursor = connection.cursor()

            try:
                # Check if the user exists and validate password
                cursor.execute(
                    "SELECT password FROM \"user\" WHERE email = %s AND semester_id = %s;",
                    (email, semester_id)
                )
                result = cursor.fetchone()
                
                if result and result[0] == password:  # Compare plaintext passwords
                    session["user"] = email
                    session["semester_id"] = semester_id

                    # Fetch subjects for the semester
                    cursor.execute(
                        "SELECT subject_id,subject_name FROM subject WHERE sem_id = %s;",
                        (semester_id,)
                    )
                    subjects = cursor.fetchall()
                    session["subjects"] = [{"id": subject[0], "name": subject[1]} for subject in subjects]


                    return redirect(url_for("user"))
                else:
                    flash("Invalid username/email or password.")
                    return redirect(url_for("loginhello"))

            except Exception as e:
                flash(f"An error occurred: {str(e)}")
                return redirect(url_for("loginhello"))

            finally:
                cursor.close()
                connection.close()
        else:
            flash("Invalid email format. Please use a valid email address.")
            return redirect(url_for("loginhello"))
    
    # Fetch semesters for the dropdown on GET request
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT semester_id, name FROM semester;")
    semesters = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("loginhello.html", semesters=semesters)

def add_user(username, email, password, semester_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        insert_query = '''
            INSERT INTO "user" (username, email, password, semester_id)
            VALUES (%s, %s, %s, %s);
        '''
        
        cursor.execute(insert_query, (username, email, password, semester_id))  # Store plaintext password
        connection.commit()
        
        print("User added successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/user")
def user():
    if "user" in session:
        subjects = session.get("subjects", [])
        return render_template("subject.html", subjects=subjects)
    else:
        return redirect(url_for("loginhello"))

@app.route("/subject/<int:subject_id>")
def subject_description(subject_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute(
        "SELECT avg_marks, description, resources FROM subject_description WHERE subject_id = %s;",
        (subject_id,)
    )
    subject_info = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if subject_info:
        avg_marks, description, resources = subject_info
        return render_template("subject_description.html", avg_marks=avg_marks, description=description, resources=resources)
    else:
        flash("Subject description not found.")
        return redirect(url_for("user"))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
