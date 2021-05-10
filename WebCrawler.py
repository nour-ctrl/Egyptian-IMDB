import requests
from bs4 import BeautifulSoup
import csv
import re
import pymysql.connections

# Function that takes cast member url and retrieves their information
def get_info(db4, db_cm, url4, mycursor4, mydb):
    url4 = str('https://elcinema.com') + url4
    r = requests.get(url4)
    soup4 = BeautifulSoup(r.content, 'html5lib')
    bio = 'NULL'
    bday = 'NULL'
    byear = 'NULL'
    pic = 'NULL'
    Nationality = 'NULL'
    for item in soup4.find_all('p', attrs={'class':'no-margin'}):
        bio = item.text.replace('...Read more', '')
    for item in soup4.find_all('a'):
        stm = str(item)
        if re.search('href="/en/index/person/nationality/.+"', stm):
            Nationality = item.text
        if re.search('href="/en/index/person/birth_day/.+"', stm):
            bday = item.text
        if re.search('href="/en/index/person/birth_year/.+"', stm):
            byear = item.text
        if pic == 'NULL':
            if re.search('/gallery/', stm):
                for img in item.find_all('img'):
                    pic = img.get('src')

    birthday = str(bday) + str(' ') + str(byear)
    if bday == str('NULL'):
        birthday = 'NULL'

    # print('Role: ', db4['Role'])
    # print('Birthday: ', birthday)
    # print('Nationality: ', Nationality)
    # print('Image: ', pic)
    # print('Bio: ', bio)
    db4['Birthday'] = birthday
    db4['Nationality'] = Nationality
    db4['Image'] = pic
    db4['Bio'] = bio
    #print(db4)
    i = 0
    status = 'Not'
    for el in db_cm:
        if db_cm[i]['ID'] == db4['ID']:
            #print('Previously appended')
            status = 'Found'
            break
            i+=1
        else:
            status = 'Not'
            i+=1
    # print('Status is ', status)
    # print('ID is ', db4['ID'])
    if status == str('Not'):
        db_cm.append(db4)
        sql = "INSERT INTO cast_info (ID, CName, Birthdate, Nationality, Image, Biography) VALUES (%s, %s, %s, %s, %s, %s)"
        mv = [(db4['ID'], db4['Member Name'], db4['Birthday'], db4['Nationality'], db4['Image'], db4['Bio'])]
        mycursor4.executemany(sql, mv)
        mydb.commit()
        #print(mycursor4.rowcount, "[Info] Was inserted")
    else:
        print('Previously appended 2')

# Function that takes movie url and retrieves cast members and invoked get_info
def get_cast(url3, db3, db_c, db_cm, mycursor3, mycursor4, mydb):
    r = requests.get(url3)
    soup3 = BeautifulSoup(r.content, 'html5lib')
    db4 = {}
    for item in soup3.findAll('div', attrs={'class':'columns small-12 min-body'}):
        #print(item)
        for item2 in item.findAll('div', attrs={'class':'row'}):
            i = 1
            role = item2.find('h3', attrs={'class':'section-title'}).text
            role = re.sub("\s\s+", " ", role)
            role = re.sub(r'\([^)]*\)', '', role)
            c = 0
            for c2 in item2.findAll('a', href=True):
                item3 = str(c2)
                t = db3['M_ID']
                db3 = {}
                db4 = {}
                db3['M_ID'] = t
                db3['Role'] = role
                if re.search('/en/person.+', item3):
                    if (c % 2) == 0:
                        c += 1
                    else:
                        cast = c2.text.replace('\n','')
                        url4 = c2.get('href')
                        id = url4.replace('/en/person/', '')
                        id = id.replace('/','')
                        db4['ID'] = id
                        db3['ID'] = id
                        print('Member: ', cast)
                        # print('Link : ', c2.get('href'))
                        db4['Member Name'] = cast
                        db4['ID'] = id
                        get_info(db4, db_cm, url4, mycursor4, mydb)
                        c +=1
                        if db3 in db_c:
                            print('Previously appended')
                        else:
                            db_c.append(db3)
                            sql = "INSERT INTO movie_cast (M_ID, CRole, ID) VALUES (%s, %s, %s)"
                            mv = [(db3['M_ID'], db3['Role'], db3['ID'])]
                            mycursor3.executemany(sql, mv)
                            mydb.commit()
                            #print(mycursor3.rowcount, "[Member] Was inserted")

# Main entry point, loops over HTML script of elcinema.com/en/boxoffice and retrieves egyptian movies
def crawler(max_year, max_week):
    year_b = 2011
    week = 1
    counter = 0
    year = '/' + str(year_b) + '/'
    db_m = []
    db_g = []
    db_c = []
    db_cm = []
    country = 'NULL'

    mydb = pymysql.connect(host='localhost',
                                     user='Nour',
                                     password='nour1234',
                                     database='egyptian_imdb'
    )
    mycursor = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()
    mycursor4 = mydb.cursor()

    while (week <= max_week) and (year_b <= max_year):
        year = '/' + str(year_b) + '/'
        print('------------------ YEAR ', year_b, '-- WEEK ', week, '-----------------------')
        url = 'https://elcinema.com/en/boxoffice' + str(year) + str(week)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        table = soup.find('div', attrs={'class': 'columns small-12 medium-7 large-8'})
        revenue = 'NULL'
        image = 'NULL'
        censorship = 'NULL'
        description = 'NULL'
        rdate = 'NULL'
        duration = 'NULL'

        for item in table.find_all('div',
                                   {'class': ['columns small-6 medium-4 large-4', 'columns small-6 medium-5 large-5']}):
            count = 0

            if item.find_all('h3'):
                for title in item.findAll('a')[1:2]:
                    db = {}
                    db2 = {}
                    print('Title: ', title.text)
                    #print('Link: ', title.get('href'))
                    #db['Link'] = title.get('href')
                    link = title.get('href').replace('/en/work/', '')
                    link = link.replace('/','')
                   # print(link)
                    db['M_ID'] = link
                    db['Title'] = title.text
                    db2['M_ID'] = link
                    url2 = 'https://elcinema.com' + str(title.get('href'))
            else:
                for value in item.findAll('li'):
                    if count == 1:
                        # print('Weekly Revenue: ', value.text)
                        # db2['Weekly Revenue'] = value.text
                        count += 1
                    elif count == 3:
                       # print('Total Revenue: ', value.text)
                        revenue = value.text
                        count += 1
                    else:
                        count += 1

                r2 = requests.get(url2)
                soup2 = BeautifulSoup(r2.content, 'html5lib')
                for img in soup2.findAll('img'):
                    img2 = str(img)
                    if re.search('https://media.elcinema.com/.+', img2):
                        image = img.get('src')
                        break

                for details in soup2.find_all('div', attrs={'class': 'columns large-10'})[1:2]:
                    desc1 = details.find('p')
                    if details.find('p') is None:
                        m = 2
                    else:
                        m = 1
                n = 5
                cens3 = ''
                for cens in details.find_all('ul')[4:5]:
                    if cens.find('a') is None:
                        for cens2 in cens.find_all('li'):
                            cens3 += str(cens2.text)
                            cens3 += str(' ')
                        # print('Censored', cens3)
                        censorship = cens3
                    for c in soup2.find_all('ul'):
                        thing = str(c)
                        if re.search('/en/index/work/country/.+', thing):
                            #print(c)
                            if re.search('class="list-separator list-title"', thing):
                                for c2 in c.findAll('a', href=True):
                                    country = c2.text

                for details in soup2.find_all('div', attrs={'class':'columns large-10'})[m:m+1]:
                    genre = []
                    date = ''
                    desc1 = details.find('p')
                    if desc1 is None:
                        description = 'NULL'
                    else:
                        desc = desc1.text.replace('...Read more', '')
                        desc = desc.replace('\n', '')
                        #print('Description:', desc)
                        description = desc

                    for rel in details.find_all('ul')[2:3]:
                        for rel1 in rel.findAll('li'):
                            rel2 = str(rel1)
                            if re.search('Egypt', rel2):
                                date = rel1.text
                                date = date.replace('Egypt', '')
                                date = date.replace('\n', '')
                                date = date.replace(']', '')
                                date = date.replace('[', '')
                                date = re.sub("\s\s+", " ", date)
                    rdate = date
                    db2['M_ID'] = db['M_ID']

                    genre1 = soup2.find('ul', attrs={'id':'jump-here-genre'})
                    if genre1 is None:
                        db2['Genre'] = 'NULL'
                    else:
                        for g in genre1.findAll('li')[1:]:
                            genre.append(g.text)
                        #print('Genre: ', genre)
                        for i in genre:
                            r = db2['M_ID']
                            db2 = {}
                            db2['M_ID'] = r
                            db2['Genre'] = i
                            if db2 not in db_g:
                                if country == 'Egypt':
                                    db_g.append(db2)
                                    sql = "INSERT INTO movie_genre (M_ID, Genre) VALUES (%s, %s)"
                                    mv = [(db2['M_ID'], db2['Genre'])]
                                    mycursor2.executemany(sql, mv)
                                    mydb.commit()
                                    #print(mycursor2.rowcount, "[Genre] Was inserted")

                for details2 in soup2.find_all('div', attrs={'class': 'columns small-9 large-10'}):
                    for dur in details2.find_all('li')[2:3]:
                        duration = dur.text

                #db['Year'] = year_b
                #db['Week'] = week
                # Title, Release Date, Duration, Censorship, Country, Total Revenue, Description, Image
                db['Release Date'] = rdate
                db['Duration'] = duration
                db['Censorship'] = censorship
                db['Country'] = country
                db['Total Revenue'] = revenue
                db['Description'] = description
                db['Image'] = image

                sql = "INSERT INTO movie (M_ID, Title, Release_Date, Duration, Censorship, Country, Total_Revenue, MDescription, Image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                rev = int(db['Total Revenue'].replace('EGP', '').replace(',', ''))
                mv = [(db['M_ID'],db['Title'], db['Release Date'], db['Duration'], db['Censorship'], db['Country'], rev, db['Description'], db['Image'])]

                i = 0
                st = 'Not'
                if country == 'Egypt':
                    print('Egyptian')
                    for el in db_m:
                        # print('Check ID ', db_cm[i]['ID'])
                        if db_m[i]['M_ID'] == db['M_ID']:
                            # print('Previously appended')
                            st = 'Found'
                            break
                            i += 1
                        else:
                            st = 'Not'
                            i += 1
                    if st == str('Not'):
                        # counter+=1
                        # print('counter is: ', counter)
                        url3 = str(url2) + str("cast")
                        db3 = {}
                        db3['M_ID'] = db['M_ID']
                        mycursor.executemany(sql, mv)
                        mydb.commit()
                        print(mycursor.rowcount, "[Movie] Was inserted")
                        get_cast(url3, db3, db_c, db_cm, mycursor3, mycursor4, mydb)
                        db_m.append(db)
                    else:
                        print('Previously appended')
                else:
                    print('Foreign')
                print('----------------------------------------------')

        week += 1
        if week == max_week+1:
            year_b += 1
            week = 1

        if year_b == 2021 and week == 14:
            break

# To put into csv files

    filename = 'movie.csv'
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, ['M_ID', 'Title', 'Release Date', 'Duration', 'Censorship', 'Country', 'Total Revenue', 'Description', 'Image'])
        w.writeheader()
        for db in db_m:
            w.writerow(db)

    filename = 'movie_genre.csv'
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, ['M_ID','Genre'])
        w.writeheader()
        for db2 in db_g:
            w.writerow(db2)

    filename = 'movie_cast.csv'
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, ['M_ID', 'Role', 'ID'])
        w.writeheader()
        for db3 in db_c:
            w.writerow(db3)

    filename = 'cast_info.csv'
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, ['ID','Member Name', 'Birthday', 'Nationality', 'Image', 'Bio'])
        w.writeheader()
        for db4 in db_cm:
            w.writerow(db4)

crawler(2021, 52)


