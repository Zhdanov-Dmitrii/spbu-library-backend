class booksUser(object):
    id_bookRead = ""
    name = ""
    author = ""
    status = ""
    genre = ""
    rate = ""
    comment = ""

    def __init__(self, id_bookRead, name, author, status,rate,comment):
        self.id_book = id_bookRead
        self.name = name
        self.author = author
        self.status = status
        self.rate = rate
        self.comment = comment

    def serialize(self):
        return {
            "id_bookRead": self.id_bookRead,
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

    def __init__(self, id_user, fio, imageUrl, email, googleId, genre):
        self.id_user = id_user
        self.fio = fio
        self.imageUrl = imageUrl
        self.email = email
        self.googleId = googleId
        self.genre = genre

    def serialize(self):
        return {
            "id_user": self.id_user,
            "fio": self.fio,
            "imageUrl": self.imageUrl,
            "email": self.email,
            "googleId": self.googleId,
            "genre": self.genre
        }


class bookInfo(object):
    id_book = ""
    name = ""
    author = ""
    genre = ""
    rate = ""

    def __init__(self, id, name, author, genre, rate):
        self.id_book = id
        self.name = name
        self.author = author
        self.genre = genre
        self.rate= rate

    def serialize(self):
        return {
            "id_book": self.id_book,
            "name": self.name,
            "author": self.author,
            "genre": self.genre,
            "rate": self.rate,
        }