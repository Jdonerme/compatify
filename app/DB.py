import os, psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
class DB(object):
    self._conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require') if os.environ['DATABASE_URL'] else None
    self._cur = self._conn.cursor() if self._conn else None
    self.initialze()

    def initialze():
        sql = """CREATE TABLE IF NOT EXISTS notifications (
                playlist_uri VARCHAR(22),
                phone_number VARCHAR(15),
                PRIMARY KEY (phone_number, playlist_uri)
            );"""
        self._cur.execute(sql)

    def getPhoneNumbersForPlaylist(playlist_uri):
        sql = "SELECT * from notifications WHERE playlist_uri = '%s" % id
        self._cur.execute(sql)
        rows = cur.fetchall()

        numbers = []
        for row in rows:
            phone_number = row[1]
            numbers.append(phone_number)
        
        return numbers

    def registerPhoneNumberToPlaylist(playlist_uri, number):
        sql = """INSERT INTO notifications (playlist_uri, phone_number)
                VALUES ('%s', '%s'); """ % (id, number)
        self._cur.execute(sql)

    
    def unsubscribePhoneNumber(number):
        sql = "DELETE FROM notifications WHERE phone_number = '%s';" % number
        self._cur.execute(sql)
    
    def removePhoneNumberFromPlaylist(playlist_uri, number):
        sql = "DELETE FROM notifications WHERE playlist_uri = '%s' AND phone_number = '%s';" % (playlist_uri, number)
        self._cur.execute(sql)
