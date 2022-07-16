from flask import Flask, make_response
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import dataTypes

app = Flask(__name__)

CORS(app)

# DB connection

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123456@localhost:5050/db_project"

db = SQLAlchemy(app)

#+
@app.route('/login/')
def login():
    googleId = request.args.get("googleId")
    fio = request.args.get("fio")
    email = request.args.get("email")
    imageUrl = request.args.get("imageUrl")

    sql_request = f"""
    SELECT "user".id_user, fio, imageUrl, email, googleId, "rule", "user".id_rule
    FROM "user" JOIN "rule" ON "user".id_rule = "rule".id_rule
    WHERE googleId = '{googleId}'
    """
    sql_result = db.engine.execute(sql_request)

    user = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], '', row[5], row[6]) for row in sql_result]
    if len(user) == 0:
        print("+++")
        sql_request = f"""
        INSERT INTO "user" (fio, imageUrl, email, googleId, id_rule)
	        VALUES ('{fio}', '{imageUrl}', '{email}', '{googleId}', 1)
        """
        sql_result = db.engine.execute(sql_request)

        sql_request = f"""
            SELECT * 
            FROM "user"
            WHERE googleId = '{googleId}'
            """
        sql_result = db.engine.execute(sql_request)
        user = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], '', row[5]) for row in sql_result]

    sql_request = f"""
    SELECT string_agg(genre.genre, ', ')
    FROM "user" join userFavoriteGenre ON "user".id_user = userFavoriteGenre.id_user
                        join genre ON userFavoriteGenre.id_genre = genre.id_genre
    WHERE "user".id_user = {user[0].id_user}
    GROUP BY "user".id_user
    """
    sql_result = db.engine.execute(sql_request)
    genre = [row for row in sql_result]

    if len(genre) == 1:
        user[0].genre = genre[0][0]

    #userLogin = UserLogin.UserLogin(user[0].id_user)
    #print(userLogin.id_user)
    #print(login_user(userLogin, True))

    return jsonify(userInfo=user[0].serialize())


#+
@app.route('/getUser/')
def getUser():
    id_user = request.args.get("id_user")

    sql_request = f"""
SELECT "user".id_user, fio, imageUrl, email, googleId, string_agg(genre.genre,', '), "rule", "user".id_rule
FROM "user" LEFT JOIN userfavoritegenre ON "user"."id_user" = userfavoritegenre."id_user"
		LEFT JOIN genre ON userfavoritegenre.id_genre = "genre"."id_genre"
		JOIN "rule" ON "rule".id_rule = "user".id_rule
WHERE "user"."id_user" = {id_user}
GROUP BY "user"."id_user", "user"."fio", "user"."email", "rule"
    """
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in sql_result]

    return jsonify(user=result[0].serialize())


@app.route('/getGenre/')
def getGenre():
    sql_request = "SELECT * FROM genre"
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.genre(row[0], row[1]) for row in sql_result]

    return jsonify(genre=[a.serialize() for a in result])


@app.route('/getUserFavoriteGenre/')
def getUserFavoriteGenre():
    user_id = request.args.get('id_user')
    sql_request = f"""
SELECT genre.id_genre, genre
FROM genre JOIN userFavoriteGenre ON genre.id_genre = userFavoriteGenre.id_genre
WHERE id_user = {user_id} 
    """
    sql_result = db.engine.execute(sql_request)

    result = [dataTypes.genre(row[0], row[1]) for row in sql_result]

    return jsonify(genre=[a.serialize() for a in result])


@app.route('/getBook/')
def getBook():
    id_book = request.args.get('id_book')

    sql_request = f"""
    SELECT book.id_book, book.name, string_agg(DISTINCT genre.genre,', '), string_agg(DISTINCT "user".fio, ', '), string_agg(DISTINCT CAST("user".id_user AS varchar(20)), ', '), AVG(bookRead.rate)
FROM book LEFT JOIN bookGenre ON book.id_book = bookGenre.id_book
   	LEFT JOIN genre ON bookGenre.id_genre = genre.id_genre
	LEFT JOIN bookAuthor ON bookAuthor.id_book = book.id_book 
	LEFT JOIN "user" ON "user".id_user = bookAuthor.id_user
   	LEFT JOIN bookRead ON book.id_book = bookRead.id_book
WHERE book.id_book ={id_book}
GROUP BY book.id_book, book.name
"""
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.bookInfo(row[0], row[1], row[2], row[3], row[4], row[5]) for row in sql_result]

    return jsonify(book=result[0].serialize())

#+
@app.route('/getBooksUser/')
def getBooksUser():
    id_user = request.args.get("id_user")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    print("getBooksUser " + id_user)

    sql_request = f"""
SELECT book.id_book, book.name, string_agg(DISTINCT "user".fio, ', '), statusRead.status, rate, comment, string_agg(DISTINCT genre.genre,', ')
FROM book LEFT JOIN bookRead ON book.id_book = bookRead.id_book
    LEFT JOIN statusRead ON bookRead.id_statusRead = statusRead.id_statusRead
    LEFT JOIN bookGenre ON book.id_book = public.bookGenre.id_book
	LEFT JOIN genre ON genre.id_genre = bookGenre.id_genre
	LEFT JOIN bookAuthor ON bookAuthor.id_book = book.id_book
	LEFT JOIN "user" ON "user".id_user = bookAuthor.id_user
WHERE bookRead.id_user = {id_user}
GROUP BY book.name,statusRead.status, rate, comment,book.id_book
                """
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.booksUser(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in sql_result]

    return jsonify(countRecord=str(len(result)),
                   booksUser=[a.serialize() for a in result[limit * page:limit * (page + 1)]])


#+
@app.route("/getUsers/")
def getUsers():
    fio = request.args.get("fio")
    email = request.args.get("email")
    genre = request.args.get("genre")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
SELECT "user".id_user, fio, imageUrl, email, googleId, string_agg(genre.genre,', '), "rule", "user".id_rule
FROM "user" LEFT JOIN userfavoritegenre ON "user"."id_user" = userfavoritegenre."id_user"
		LEFT JOIN genre ON userfavoritegenre.id_genre = "genre"."id_genre"
		JOIN "rule" ON "rule".id_rule = "user".id_rule
WHERE "user".fio like '%%{fio}%%'
and "user".email like '%%{email}%%'
GROUP BY "user".id_user, "user".fio, "user".email, "rule"
"""

    if genre != '':
        sql_request += f"HAVING string_agg(genre.name,', ') like '%%{genre}%%'"

    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in sql_result]

    resp = make_response(jsonify(countRecord=str(len(result)),
                                 users=[a.serialize() for a in result[limit * page:limit * (page + 1)]]))
    resp.set_cookie('same-site-cookie', 'foo', samesite='Lax')
    # Ensure you use "add" to not overwrite existing cookie headers
    resp.headers.add('Set-Cookie', 'cross-site-cookie=bar; SameSite=None; Secure')
    return resp

#+
@app.route("/getBooks/")
def getBooks():
    print("qwdfrs")
    name = request.args.get("name")
    author = request.args.get("author")
    genre = request.args.get("genre")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
SELECT book.id_book, book.name, string_agg(DISTINCT genre.genre,', '), string_agg(DISTINCT "user".fio, ', '), string_agg(DISTINCT CAST("user".id_user AS varchar(20)), ', '), AVG(bookRead.rate)
FROM book LEFT JOIN bookGenre ON book.id_book = bookGenre.id_book
   	LEFT JOIN genre ON bookGenre.id_genre = genre.id_genre
	LEFT JOIN bookAuthor ON bookAuthor.id_book = book.id_book 
	LEFT JOIN "user" ON "user".id_user = bookAuthor.id_user
   	LEFT JOIN bookRead ON book.id_book = bookRead.id_book
WHERE book.name like '%%{name}%%'
GROUP BY book.id_book, book.name
HAVING string_agg(DISTINCT genre.genre,', ') like '%%{genre}%%' and string_agg(DISTINCT "user".fio, ', ') LIKE '%%{author}%%' """

    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.bookInfo(row[0], row[1], row[2], row[3], row[4], row[5]) for row in sql_result]

    return jsonify(countRecord=str(len(result)),
                   books=[a.serialize() for a in result[limit * page:limit * (page + 1)]])


#-
@app.route('/addRead/', methods=["POST"])
def addRead():
    id_book = request.form["id_book"]
    id_user = request.form["id_user"]
    rate = request.form["rate"]
    comment = request.form["comment"]
    status = request.form["status"]

    sql_request = f"""
INSERT INTO bookRead(id_statusRead, id_book, id_user, rate, comment)
	VALUES ({status}, {id_book}, {id_user}, {rate}, '{comment}')
ON CONFLICT (id_book, id_user) DO UPDATE
	SET id_statusRead = {status},
		rate = {rate},
		comment = '{comment}'
	"""

    db.engine.execute(sql_request)

    print(1)

    return jsonify(res=1)


#+
@app.route('/getReadUsers/')
def getReadUsers():
    id_book = request.args.get("id_book")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
SELECT "user".id_user, "user".fio, "user".imageUrl, "user".email, "user".googleId, 
	string_agg(DISTINCT genre.genre,', '), bookRead.rate, bookRead.comment
FROM bookRead JOIN "user" ON bookRead.id_user = "user".id_user
		LEFT JOIN userFavoriteGenre ON userFavoriteGenre.id_user = "user".id_user
		LEFT JOIN genre ON userFavoriteGenre.id_genre = genre.id_genre
where bookRead.id_book = {id_book}
GROUP BY "user".id_user, "user".fio, "user".imageUrl,"user".email, "user".googleId, 
          bookRead.rate, bookRead.comment
    """

    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.readUsers(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in sql_result]

    return jsonify(countRecord=str(len(result)),
                   readUsers=[a.serialize() for a in result[limit * page:limit * (page + 1)]])


@app.route('/addUser/', methods=["POST"])
def addUser():
    fio = request.form["fio"]
    imageUrl = request.form["imageUrl"]
    email = request.form["email"]
    googleId = request.form["googleId"]
    id_rule = request.form["id_rule"]

    favoriteGenre = request.form["favoriteGenre"].split(',')
    print(favoriteGenre)

    sql_request = f"""
INSERT INTO "user" (fio, imageUrl, email, googleId, id_rule) VALUES 
    ('{fio}','{imageUrl}', '{email}', '{googleId}', {id_rule})
    """
    db.engine.execute(sql_request)

    sql_request = f"""
    SELECT id_user FROM "user"
    WHERE fio = '{fio}' AND imageUrl = '{imageUrl}' AND email = '{email}' AND googleId = '{googleId}' AND id_rule = {id_rule}
    """
    sql_result = db.engine.execute(sql_request)
    id_user = [row[0] for row in sql_result]
    id_user = id_user[0]

    insert = ""
    for id_genre in favoriteGenre:
        insert += "("+str(id_user)+","+id_genre+"),\n"
    insert = insert[:-2]

    sql_request = f"""
    DELETE FROM public.userfavoritegenre
	WHERE id_user = {id_user};
INSERT INTO userFavoriteGenre (id_user, id_genre) VALUES {insert}
    """
    print(sql_request)
    db.engine.execute(sql_request)

    return jsonify(res=1)


@app.route('/updateUser/', methods=["POST"])
def updateUser():
    id_user = request.form["id_user"]
    fio = request.form["fio"]
    imageUrl = request.form["imageUrl"]
    email = request.form["email"]
    googleId = request.form["googleId"]
    id_rule = request.form["id_rule"]

    favoriteGenre = request.form["favoriteGenre"].split(',')

    sql_request = f"""
    UPDATE "user"
	SET fio='{fio}', imageurl='{imageUrl}', email='{email}', googleid='{googleId}', id_rule={id_rule}
	WHERE id_user = {id_user};
	"""
    db.engine.execute(sql_request)

    insert = ""
    for id_genre in favoriteGenre:
        insert += "(" + str(id_user) + "," + id_genre + "),\n"
    insert = insert[:-2]

    sql_request = f"""
        DELETE FROM public.userfavoritegenre
    	WHERE id_user = {id_user};
    INSERT INTO userFavoriteGenre (id_user, id_genre) VALUES {insert}
        """
    db.engine.execute(sql_request)

    return jsonify(res=1)


@app.route('/setRule/', methods=["POST"])
def setRule():
    id_user = request.form["id_user"]
    id_rule = request.form["id_rule"]

    sql_request = f"""
    UPDATE "user"
	SET id_rule={id_rule}
	WHERE id_user = {id_user};
	"""
    db.engine.execute(sql_request)
    return jsonify(res=1)


@app.route('/getBooksAuthor/')
def getBooksAuthor():
    id_user = request.args.get("id_user")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
    SELECT book.id_book, book.name, string_agg(DISTINCT genre.genre,', '), string_agg(DISTINCT "user".fio, ', '), string_agg(DISTINCT CAST("user".id_user AS varchar(20)), ', '), AVG(bookRead.rate)
    FROM book LEFT JOIN bookGenre ON book.id_book = bookGenre.id_book
       	LEFT JOIN genre ON bookGenre.id_genre = genre.id_genre
    	LEFT JOIN bookAuthor ON bookAuthor.id_book = book.id_book 
    	LEFT JOIN "user" ON "user".id_user = bookAuthor.id_user
       	LEFT JOIN bookRead ON book.id_book = bookRead.id_book
    WHERE bookAuthor.id_user = {id_user}
    GROUP BY book.id_book, book.name
"""
    print(sql_request)

    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.bookInfo(row[0], row[1], row[2], row[3], row[4], row[5]) for row in sql_result]

    return jsonify(countRecord=str(len(result)),
                   books=[a.serialize() for a in result[limit * page:limit * (page + 1)]])


@app.route('/getBookGenre')
def getBookGenre():
    id_book = request.args.get("id_book")


    sql_request = f"""
SELECT genre.id_genre, genre
FROM genre JOIN bookGenre ON genre.id_genre = bookGenre.id_genre
WHERE id_book = {id_book}
    """
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.genre(row[0], row[1]) for row in sql_result]

    return jsonify(genre=[a.serialize() for a in result])


@app.route('/addBook/', methods=["POST"])
def addBook():
    name = request.form["name"]
    bookGenre = request.form["bookGenre"].split(',')
    bookAuthor = request.form["bookAuthor"].split(',')

    sql_request = f"""
    INSERT INTO book (name) VALUES ('{name}')
            """
    sql_result = db.engine.execute(sql_request)

    sql_request = f"""
        SELECT id_book FROM book
        WHERE name = '{name}'
        """
    sql_result = db.engine.execute(sql_request)
    id_book = [row[0] for row in sql_result]
    id_book = id_book[0]


    insert = f"""
    DELETE FROM bookGenre
	WHERE id_book = {id_book};
    INSERT INTO bookGenre (id_book,id_genre) VALUES 
    """
    for id_genre in bookGenre:
        insert += "(" + str(id_book) + "," + id_genre + "),\n"
    insert = insert[:-2]
    insert +=';\n'

    insert += f"""
    DELETE FROM bookAuthor
    WHERE id_book = {id_book};
    INSERT INTO bookAuthor (id_book, id_user) VALUES 
    """

    for id_user in bookAuthor:
        insert += "(" + str(id_book) + "," + id_user + "),\n"
    insert = insert[:-2]
    print(insert)
    db.engine.execute(insert)

    return jsonify(res=1)


@app.route('/updateBook/', methods=["POST"])
def updateBook():
    id_book = request.form["id_book"]
    name = request.form["name"]
    bookGenre = request.form["bookGenre"].split(',')
    bookAuthor = request.form["bookAuthor"].split(',')


    insert = f"""
    INSERT INTO book (name) VALUES ('{name}');
    DELETE FROM bookGenre
	WHERE id_book = {id_book};
    INSERT INTO bookGenre (id_book,id_genre) VALUES 
    """
    for id_genre in bookGenre:
        insert += "(" + str(id_book) + "," + id_genre + "),\n"
    insert = insert[:-2]
    insert +=';\n'

    insert += f"""
    DELETE FROM bookAuthor
    WHERE id_book = {id_book};
    INSERT INTO bookAuthor (id_book, id_user) VALUES 
    """

    for id_user in bookAuthor:
        insert += "(" + str(id_book) + "," + id_user + "),\n"
    insert = insert[:-2]
    print(insert)
    db.engine.execute(insert)

    return jsonify(res=1)


if __name__ == "__main__":
    app.run()
