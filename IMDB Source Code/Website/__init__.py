from flask import Flask, render_template, request, flash, redirect
from flask_mysqldb import MySQL 
import re


app = Flask (__name__)

# app.config['MYSQL_USER'] = 'Nour'
# app.config['MYSQL_PASSWORD'] = 'nour1234'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_DB'] = 'egyptian_imdb'

######### TO USE REMOTELY ##############
app.config['MYSQL_USER'] = 'sql5410672'
app.config['MYSQL_PASSWORD'] = '18aGlaB9vl'
app.config['MYSQL_HOST'] = 'sql5.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql5410672'


app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


def create_app(): 
    app.config['SECRET_KEY'] = 'randomstring'

    from .views import views 
    from .auth import auth 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app

######### Sign Up Page ##############
@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        gender = request.form.get('gender')
        birthdate = request.form.get('birthdate')
        age = request.form.get('age')

        if len(email) < 4:
            flash('Email Invalid: must be greater than 7 characters', category='error')
        elif len(username) < 4:
            flash('Username Invalid: must be greater than 4 characters', category='error')
        elif len(password) < 4:
            flash('Password Invalid: must be greater than 4 characters', category='error')
        elif len(gender) < 1:
            flash('Gender Invalid: you must pick an option', category='error')
        elif len(birthdate) < 4:
            flash('Birthdate Invalid: must be greater than 4 characters', category='error')
        elif len(age) < 1:
            flash('Age Invalid: must be greater than 1 character', category='error')
        else:
            cur.execute("INSERT INTO users (email, username, gender, age, birthdate, password) VALUES (%s, %s, %s, %s, %s, %s)", (email, username, gender, age, birthdate, password))
            mysql.connection.commit()
            cur.close()
            print('SUCESS')
            flash('Account successfully created!', category='success')

    return render_template("sign_up.html")

######### Login Page: Checks if email and password are valid by retrieving user data ##############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        email = request.form.get('email')
        password = request.form.get('password')
        cur.execute("SELECT Email, password FROM users")
        emails = cur.fetchall()
        if len(email) > 4:
            for n in emails: 
                if n['Email'] == email: 
                    print(n)
                    print ('Found')
                    if n['password'] == password:
                        print('Logging in')
                        flash('Logging in', category='success')
                        return redirect('/home')
                    else:
                        print('wrong password')
                        flash('Wrong password, try again', category='error')
                else: 
                    print('not')
            flash('The email you entered does not belong to an account. Sign up!', category='error')
            
    return render_template("login.html")

######### Home Page ##############
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        search = request.form.get('search')
        return redirect('/'+ str(search))
    
    count = 0
    count1 = 0
    current = {}
    last_year = {}
    movie_ID = {}
    movie_ID2 = {}
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movie")
    movies = cur.fetchall()
    
    for m in movies:
        if m['Release_Date'].find(' 2021') != -1: 
            current[count] = m['Image']
            movie_ID[count] = m['M_ID']
            count+=1
        elif m['Release_Date'].find(' 2020') != -1:
            last_year[count1] = m['Image']
            movie_ID2[count1] = m['M_ID']
            count1+=1
    return render_template("home.html", len=len(current), current=current, len1=len(last_year), last_year=last_year, movie_ID=movie_ID, movie_ID2=movie_ID2)

######### All Movies Page ##############
@app.route('/movies')
def all():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        search = request.form.get('search')
        return redirect('/'+ str(search))

    count=0
    movie_img = {}
    movie_id = {}
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movie")
    all_movies = cur.fetchall()
    
    for m in all_movies: 
        movie_img[count] = m['Image']
        movie_id[count] = m['M_ID']
        count+=1
    title = "All Movies"
    return render_template("all.html", title=title, movie_img=movie_img, movie_id=movie_id, len=len(movie_id))

######### All Cast Page ##############
@app.route('/cast')
def allcast():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        search = request.form.get('search')
        return redirect('/'+ str(search))

    count=0
    cast_img = {}
    cast_id = {}
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cast_info")
    all_movies = cur.fetchall()
    
    for m in all_movies: 
        cast_img[count] = m['Image']
        cast_id[count] = m['ID']
        count+=1
    return render_template("allcast.html", cast_img=cast_img, cast_id=cast_id, len=len(cast_id))


######### Top 10 Movies Page ##############
@app.route('/top')
def top_movies():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        search = request.form.get('search')
        return redirect('/'+ str(search))

    count=0
    movie_img = {}
    movie_id = {}
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movie ORDER BY Total_Revenue DESC LIMIT 10")
    tmovies = cur.fetchall()

    for m in tmovies: 
        movie_img[count] = m['Image']
        movie_id[count] = m['M_ID']
        count+=1
    title = "Top 10 Movies"
    return render_template("all.html",title=title, movie_img=movie_img, movie_id=movie_id, len=len(movie_id))

######### Checks if string is a movie/cast ID  ##############
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

######### Movie, and Genre Pages ##############
@app.route('/<mov>', methods=['GET', 'POST'])
def movies(mov):
    # if the string has numbers then it is a movie ID, else it is a genre
    if hasNumbers(mov) == True: 
        # inserts review into 'watches' table in database
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            email=request.form.get('email')
            review=request.form.get('review')
            rating=request.form.get('rating')

            if len(review) < 3:
                flash('Review invalid, try again', category='error')
            elif len(email) < 4:
                flash('Email Invalid: must be greater than 7 characters', category='error')
            else:
                cur.execute("INSERT INTO watches (email, review, rating, M_ID) VALUES (%s, %s, %s, %s)", (email, review, rating, mov))
                mysql.connection.commit()
                cur.close()
                print('SUCESS')
                flash('Review successfully created!', category='success')
            
        count=0
        count2=0
        movie = {}
        info = {}
        role = {}
        gen = {}
        
        cur = mysql.connection.cursor()

        cur.execute("SELECT *, format(Total_Revenue,'0,###.##') AS Comma FROM movie")   # formats revenue to have commas
        all_movies = cur.fetchall()

        cur.execute("SELECT AVG(Rating) AS rate FROM watches WHERE M_ID =%s", [mov])    # calculates the average of user movie ratings
        rate=cur.fetchall()
        r1 = str(rate)
        
        if hasNumbers(r1) == True:
            r = str(rate[0])
            res = re.findall(r"'(.*?)'", r, re.DOTALL)
            rate = res[1]
            print(res)
        else: 
            rate = 'NULL'

        cur.execute("SELECT C.ID, C.CRole FROM movie_cast C WHERE C.M_ID = %s", [mov])
        m_cast = cur.fetchall()

        cur.execute("SELECT * FROM cast_info")
        allcast = cur.fetchall()

        cur.execute("SELECT * FROM watches WHERE M_ID =%s", [mov])
        reviews=cur.fetchall()

        cur.execute("SELECT Genre FROM movie_genre WHERE M_ID=%s", [mov])
        genre=cur.fetchall()

        for m in all_movies: 
            if m['M_ID'] == mov:
                movie = m 
        for c in allcast: 
            for c2 in m_cast: 
                if c2['ID'] == c['ID']:
                    info [count] = c
                    role[count] = c2['CRole']
                    count+=1
        for g in genre:
            gen[count2] = g['Genre']
            count2+=1
        return render_template("movie.html", movie=movie, info=info, len1=len(info), reviews=reviews, len2=len(reviews), rate=rate, role=role, genre=gen, len_g=len(gen))

    else: 
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            search = request.form.get('search')
            return redirect('/'+ str(search))
        else: 
            m_img = {}
            m_id = {}
            count = 0
            mov2 = mov+str(" ")
            cur = mysql.connection.cursor()

            cur.execute("SELECT M.M_ID, Image FROM movie_genre G, movie M WHERE Genre=%s and M.M_ID = G.M_ID", [mov2])
            allmovies = cur.fetchall()
            
            for m in allmovies: 
                m_img[count]= m['Image']
                m_id[count] = m['M_ID']
                count+=1
            return render_template ("genre.html", m_img=m_img, len=len(m_img), genre=mov.capitalize(), m_id=m_id)


######### Years ##############
@app.route('/year/<c_year>')
def year(c_year):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        search = request.form.get('search')
        return redirect('/'+ str(search))

    count=0
    movie_img = {}
    movie_id = {}
    cur = mysql.connection.cursor()

    cur.execute("SELECT M_ID, Image FROM movie WHERE Release_Date LIKE '%"+c_year+"%'")
    info=cur.fetchall()
   
    for m in info: 
        movie_img[count] = m['Image']
        movie_id[count] = m['M_ID']
        count+=1
    title = c_year + str(" Movies")
    return render_template("all.html",title=title, movie_img=movie_img, movie_id=movie_id, len=len(movie_id))

######### Cast Members ##############
@app.route('/cast/<member_ID>')
def cast(member_ID):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        search = request.form.get('search')
        return redirect('/'+ str(search))

    c_info = {}
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM cast_info WHERE ID =%s", [member_ID])
    info=cur.fetchall()

    cur.execute("SELECT M.M_ID, M.Image FROM movie M, movie_cast C WHERE C.ID =%s and M.M_ID = C.M_ID", [member_ID])
    c_movie = cur.fetchall()
    
    for i in info: 
        if i['ID'] == member_ID:
            c_info = i
    return render_template("cast.html", info=c_info, c_movie=c_movie, len1=len(c_movie))