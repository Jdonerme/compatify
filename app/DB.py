import os, psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
class DB(object):
    self._conn = psycopg2.connect(os.environ['DATABASE_URL'], sslmode='require') if os.environ['DATABASE_URL'] else None
    self._cur = self._conn.cursor() if self._conn else None
    self.initialze()

    def initialze():
        sql = "CREATE TABLE IF NOT EXISTS CREATE TABLE test;" #... TODO
        # cur.execute(sql)

    def getPhoneNumbersForPlaylist(playlist_uri):
        # TODO
        numbers = []
        return numbers

    def registerPhoneNumberToPlaylist(playlist_uri, number):
        # TODO
    
    def unsubscribePhoneNumber(number):
        #TODO
    
    def removePhoneNumberFromPlaylist(playlist_uri, number):
        # TODO
