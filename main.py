from flask import Flask
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS
import time
import dataTypes

import urllib

app = Flask(__name__)
CORS(app)

# DB connection

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123456@localhost:5050/librarySPBU"
db = SQLAlchemy(app)


@app.route('/login/')
def login():
    googleId = request.args.get("googleId")
    fio = request.args.get("fio")
    email = request.args.get("email")
    imageUrl = request.args.get("imageUrl")

    sql_request = f"""
    SELECT * 
    FROM "public.user"
    WHERE "googleId" = '{googleId}'
    """
    print(sql_request)
    sql_result = db.engine.execute(sql_request)

    user = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4],'') for row in sql_result]
    if len(user) == 0:
        print("+++")
        sql_request = f"""
        INSERT INTO public."public.user"("fio", "imageUrl", "email", "googleId")
	        VALUES ('{fio}', '{imageUrl}', '{email}', '{googleId}')
        """
        print(sql_request)
        sql_result = db.engine.execute(sql_request)

        sql_request = f"""
            SELECT * 
            FROM "public.user"
            WHERE "googleId" = '{googleId}'
            """
        sql_result = db.engine.execute(sql_request)
        user = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4],'') for row in sql_result]
        print(len(user))

    sql_request = f"""
    SELECT string_agg("public.genre"."name", ', ')
    FROM "public.user" join "public.userFavoriteGenre" ON "public.user".id_user="public.userFavoriteGenre".id_user
                        join "public.genre" ON "public.userFavoriteGenre".id_genre = "public.genre"."id_genre"
    WHERE "public.user".id_user = {user[0].id_user}
    GROUP BY "public.user".id_user
    """
    print(user[0].id_user)
    sql_result = db.engine.execute(sql_request)
    genre = [row for row in sql_result]
    print(sql_request)

    if len(genre) == 1:
        user[0].genre = genre[0][0]

    print(user[0].serialize())
    return jsonify(userInfo=user[0].serialize())


@app.route('/getBooksUser/')
def getBooksUser():
    id_user = request.args.get("id_user")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
SELECT "id_bookRead", "public.book"."name", "public.book"."author","public.statusRead"."status", "rate", "comment"
FROM "public.book" JOIN "public.bookRead" ON "public.book".id_book = "public.bookRead".id_book
				   JOIN "public.statusRead" 
				   ON "public.bookRead".status = "public.statusRead"."id_statusRead"
WHERE "id_user" = {id_user}
                """
    print(sql_request)
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.booksUser(row[0],row[1],row[2],row[3],row[4], row[5]) for row in sql_result]

    for row in result:
        sql_request = f"""
        SELECT string_agg("public.genre"."name",', ')
 from "public.bookRead" JOIN "public.book" ON "public.bookRead"."id_book" = "public.book"."id_book"
 	JOIN "public.bookGenre" ON "public.book"."id_book" = "public.bookGenre"."id_book"
 	JOIN "public.genre" ON "public.bookGenre"."id_genre" = "public.genre"."id_genre"
WHERE "public.bookRead"."id_book" = {row.id_book} and "id_user" = {id_user}
        """

        sql_result = db.engine.execute(sql_request)
        genre = [a[0] for a in sql_result]
        if(len(genre) > 0):
            row.genre = genre[0]

    return jsonify(countRecord=str(len(result)),
                   booksUser=[a.serialize() for a in result[limit * page:limit * (page + 1)]])


@app.route("/getBooks/")
def getBooks():
    name = request.args.get("name")
    author = request.args.get("author")
    genre = request.args.get("genre")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
    SELECT "public.book"."id_book", "public.book"."name", "public.book"."author", string_agg("public.genre"."name",', ') , AVG("public.bookRead"."rate")
FROM "public.book" JOIN "public.bookGenre" ON "public.book"."id_book" = "public.bookGenre"."id_book"
 	JOIN "public.genre" ON "public.bookGenre"."id_genre" = "public.genre"."id_genre"
	JOIN "public.bookRead" ON "public.book"."id_book" ="public.bookRead"."id_book"
WHERE "public.book"."name" like '%%{name}%%'
and "public.book"."author" like '%%{author}%%'
GROUP BY "public.book"."id_book", "public.book"."name", "public.book"."author"
HAVING string_agg("public.genre"."name",', ') like '%%{genre}%%' """

    print(sql_request)
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.bookInfo(row[0], row[1], row[2],row[3], row[4]) for row in sql_result]


    return jsonify(countRecord=str(len(result)),
                   books=[a.serialize() for a in result[limit * page:limit * (page + 1)]])



@app.route("/getUsers/")
def getUsers():
    fio = request.args.get("fio")
    email = request.args.get("email")
    genre = request.args.get("genre")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
SELECT "public.user".id_user, fio, "imageUrl", email, "googleId", string_agg("public.genre"."name",', ')
FROM "public.user" JOIN "public.userFavoriteGenre" ON "public.user"."id_user" = "public.userFavoriteGenre"."id_user"
		JOIN "public.genre" ON "public.userFavoriteGenre"."id_genre" = "public.genre"."id_genre"
WHERE "public.user"."fio" like '%%{fio}%%'
and "public.user"."email" like '%%{email}%%'
GROUP BY "public.user"."id_user", "public.user"."fio", "public.user"."email"
HAVING string_agg("public.genre"."name",', ') like '%%{genre}%%'
"""

    print(sql_request)
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], row[5]) for row in sql_result]

    return jsonify(countRecord=str(len(result)),
                   users=[a.serialize() for a in result[limit * page:limit * (page + 1)]])



if __name__ == "__main__":
    app.run(debug=True)