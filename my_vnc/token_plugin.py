import sqlite3
class dbToken(BasePlugin):
    def lookup(self, token):
        db = sqlite3.connect(self.source)
        db.row_factory = sqlite3.Row
        cursor = db.execute("SELECT * FROM tokens WHERE tokenname = ?", (token,))
        row = cursor.fetchone()
        db.close()
        if not row:
            return None
        return [row['tokenip'].encode().strip(), "5900"]
