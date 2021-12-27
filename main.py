from flask import Flask, make_response
from flask import request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required
import dataTypes
import UserLogin
import urllib


app = Flask(__name__)


CORS(app)


app.config['SECRET_KEY'] = 'mfsdkfm;efj;ldkfm;kdjfne;fmdsjfn;aefma;ksdfmcs;djns;'

# DB connection

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123456@localhost:5050/librarySPBU"


db = SQLAlchemy(app)

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin.UserLogin(user_id)


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
    sql_result = db.engine.execute(sql_request)

    user = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], '') for row in sql_result]
    if len(user) == 0:
        print("+++")
        sql_request = f"""
        INSERT INTO public."public.user"("fio", "imageUrl", "email", "googleId")
	        VALUES ('{fio}', '{imageUrl}', '{email}', '{googleId}')
        """
        sql_result = db.engine.execute(sql_request)

        sql_request = f"""
            SELECT * 
            FROM "public.user"
            WHERE "googleId" = '{googleId}'
            """
        sql_result = db.engine.execute(sql_request)
        user = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], '') for row in sql_result]

    sql_request = f"""
    SELECT string_agg("public.genre"."name", ', ')
    FROM "public.user" join "public.userFavoriteGenre" ON "public.user".id_user="public.userFavoriteGenre".id_user
                        join "public.genre" ON "public.userFavoriteGenre".id_genre = "public.genre"."id_genre"
    WHERE "public.user".id_user = {user[0].id_user}
    GROUP BY "public.user".id_user
    """
    sql_result = db.engine.execute(sql_request)
    genre = [row for row in sql_result]

    if len(genre) == 1:
        user[0].genre = genre[0][0]

    userLogin = UserLogin.UserLogin(user[0].id_user)
    print(userLogin.id_user)
    print(login_user(userLogin, True))
    print(current_user.get_id())

    return jsonify(userInfo=user[0].serialize())


@app.route('/getBooksUser/')
def getBooksUser():
    id_user = request.args.get("id_user")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    print("getBooksUser " + id_user)

    sql_request = f"""
SELECT "id_bookRead", "public.book"."name", "public.book"."author","public.statusRead"."status", "rate", "comment", string_agg(DISTINCT "public.genre"."name",', ')
FROM "public.book" JOIN "public.bookRead" ON "public.book".id_book = "public.bookRead".id_book
		JOIN "public.statusRead" ON "public.bookRead".status = "public.statusRead"."id_statusRead"
		LEFT JOIN "public.bookGenre" ON "public.book"."id_book" = "public.bookGenre"."id_book"
		JOIN "public.genre" ON "public.genre".id_genre = "public.bookGenre"."id_genre"
WHERE "id_user" = {id_user}
GROUP BY "id_bookRead", "public.book"."name", "public.book"."author","public.statusRead"."status", "rate", "comment"
                """
    print(sql_request)
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.booksUser(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in sql_result]

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
    SELECT "public.book"."id_book", "public.book"."name", "public.book"."author", string_agg(DISTINCT "public.genre"."name",', ') , AVG("public.bookRead"."rate")
FROM "public.book" JOIN "public.bookGenre" ON "public.book"."id_book" = "public.bookGenre"."id_book"
 	JOIN "public.genre" ON "public.bookGenre"."id_genre" = "public.genre"."id_genre"
	LEFT JOIN "public.bookRead" ON "public.book"."id_book" ="public.bookRead"."id_book"
WHERE "public.book"."name" like '%%{name}%%'
and "public.book"."author" like '%%{author}%%'
GROUP BY "public.book"."id_book", "public.book"."name", "public.book"."author"
HAVING string_agg("public.genre"."name",', ') like '%%{genre}%%' """

    print(sql_request)
    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.bookInfo(row[0], row[1], row[2], row[3], row[4]) for row in sql_result]

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

    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.userInfo(row[0], row[1], row[2], row[3], row[4], row[5]) for row in sql_result]

    resp = make_response(jsonify(countRecord=str(len(result)),
                                 users=[a.serialize() for a in result[limit * page:limit * (page + 1)]]))
    resp.set_cookie('same-site-cookie', 'foo', samesite='Lax')
    # Ensure you use "add" to not overwrite existing cookie headers
    resp.headers.add('Set-Cookie', 'cross-site-cookie=bar; SameSite=None; Secure')
    return resp


@app.route('/addRead/', methods=["POST"])
def addRead():
    id_book = request.form["id_book"]
    id_user = request.form["id_user"]
    rate = request.form["rate"]
    comment = request.form["comment"]
    status = request.form["status"]


    sql_request = f"""INSERT INTO public."public.bookRead"(
	status, id_book, id_user, rate, comment)
	VALUES ({status}, {id_book}, {id_user}, {rate}, '{comment}')
	WHERE NOT EXISTS (SELECT * FROM public."public.bookRead" WHERE id_user = {id_user} AND id_book = {id_book})"""

    db.engine.execute(sql_request)

    print(1)

    return jsonify(res=1)


@app.route('/getReadUsers/')
def getReadUsers():
    id_book = request.args.get("id_book")
    limit = int(request.args.get("limit"))
    page = int(request.args.get("page"))

    sql_request = f"""
SELECT "public.user".id_user, "public.user".fio, "public.user"."imageUrl", "public.user".email, "public.user"."googleId", 
	string_agg(DISTINCT "public.genre"."name",', '), "public.bookRead".rate, "public.bookRead".comment
FROM "public.bookRead" JOIN "public.user" ON "public.bookRead".id_user = "public.user".id_user
		JOIN "public.userFavoriteGenre" ON "public.userFavoriteGenre".id_user = "public.user".id_user
		JOIN "public.genre" ON "public.userFavoriteGenre".id_genre = "public.genre".id_genre
where "public.bookRead"."id_book" = {id_book}
GROUP BY "public.user".id_user, "public.user".fio, "public.user"."imageUrl","public.user".email, "public.user"."googleId", 
          "public.bookRead".rate, "public.bookRead".comment
    """

    sql_result = db.engine.execute(sql_request)
    result = [dataTypes.readUsers(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]) for row in sql_result]

    return jsonify(countRecord=str(len(result)),
                   readUsers=[a.serialize() for a in result[limit * page:limit * (page + 1)]])


if __name__ == "__main__":
    app.run()

