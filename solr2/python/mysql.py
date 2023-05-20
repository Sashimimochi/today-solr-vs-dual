import pymysql

class MySQLClient:
    def __init__(self) -> None:
        pass

    def select_lcc(self):
        query = f'''
            SELECT id, media, url, created_at, title, body
            FROM lcc
        '''
        return self._select(query)

    def select_knbc(self):
        query = f'''
            SELECT id, doc, emotion
            FROM knbc
        '''
        return [
            {
                'id': row.get('id'),
                'media': None,
                'url': None,
                'created_at': None,
                'title': row.get('emotion'),
                'body': row.get('doc')
            } for row in self._select(query)
        ]
    
    def select_kwdlc(self):
        query = f'''
            SELECT id, body
            FROM kwdlc
        '''
        return [
            {
                'id': row.get('id'),
                'media': None,
                'url': None,
                'created_at': None,
                'title': None,
                'body': row.get('body')
            } for row in self._select(query)
        ]
    
    def select_with_query(self, query):
        return self._select(query)

    def select(self, topK:int=None):
        data = []
        data += self.select_lcc()
        data += self.select_knbc()
        data += self.select_kwdlc()
        return data[:topK] if topK else data

    def _select(self, query):
        cnx = None
        res = None

        try:
            cnx = pymysql.connect(
                user='solrtutorial',
                password='solrtutorial',
                host='mysql',
                database='lcc',
                cursorclass=pymysql.cursors.DictCursor
            )

            cursor = cnx.cursor()

            cursor.execute(query)

            res = cursor.fetchall()

            cursor.close()
        except Exception as e:
            res = e
            raise Exception(e)
        finally:
            if cnx:
                cnx.close()
            return res
