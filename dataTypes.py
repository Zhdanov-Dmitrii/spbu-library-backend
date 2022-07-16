class genre(object):
    id_genre = ""
    genre = ""

    def __init__(self, id_genre, genre):
        self.genre = genre
        self.id_genre = id_genre

    def serialize(self):
        return {
            "id_genre": self.id_genre,
            "genre": self.genre
        }


class booksUser(object):
    name = ""
    author = ""
    status = ""
    genre = ""
    rate = ""
    comment = ""

    def __init__(self, id_book, name, author, status,rate,comment, genre):
        self.id_book = id_book
        self.name = name
        self.author = author
        self.status = status
        self.rate = rate
        self.comment = comment
        self.genre = genre

    def serialize(self):
        return {
            "id_book": self.id_book,
            "name": self.name,
            "author": self.author,
            "status": self.status,
            "genre": self.genre,
            "rate": self.rate,
            "comment": self.comment
        }


class userInfo(object):
    id_user = ""
    googleId = ""
    fio = ""
    email = ""
    imageUrl = ""
    genre = ""
    rule = ""
    id_rule = ""

    def __init__(self, id_user, fio, imageUrl, email, googleId, genre, rule, id_rule):
        self.id_user = id_user
        self.fio = fio
        self.imageUrl = imageUrl
        self.email = email
        self.googleId = googleId
        self.genre = genre
        self.rule = rule
        self.id_rule = id_rule

    def serialize(self):
        return {
            "id_user": self.id_user,
            "fio": self.fio,
            "imageUrl": self.imageUrl,
            "email": self.email,
            "googleId": self.googleId,
            "genre": self.genre,
            "rule": self.rule,
            "id_rule": self.id_rule
        }


class bookInfo(object):
    id_book = ""
    name = ""
    genre = ""
    authors = [""]
    id_authors = [""]
    rate = ""

    def __init__(self, id, name, genre, authors, id_authors, rate):
        self.id_book = id
        self.name = name
        self.authors = authors.split(', ')
        self.id_authors = id_authors.split(', ')
        self.genre = genre
        self.rate = rate

    def serialize(self):
        return {
            "id_book": self.id_book,
            "name": self.name,
            "authors": self.authors,
            "id_authors": self.id_authors,
            "genre": self.genre,
            "rate": self.rate,
        }


class readUsers(object):
    id_user = ""
    fio = ""
    imageUrl = ""
    email = ""
    googleId = ""
    genre = ""
    rate = ""
    comment = ""

    def __init__(self, id_user, fio, imageUrl, email, google_id, genre, rate, comment):
        self.id_user = id_user
        self.fio = fio
        self.imageUrl =imageUrl
        self.email = email
        self.googleId = google_id
        self.genre = genre
        self.rate = rate
        self.comment = comment


    def serialize(self):
        return {
            "id_user": self.id_user,
            "fio": self.fio,
            "imageUrl": self.imageUrl,
            "email": self.email,
            "googleId": self.googleId,
            "genre": self.genre,
            "rate": self.rate,
            "comment": self.comment
        }
