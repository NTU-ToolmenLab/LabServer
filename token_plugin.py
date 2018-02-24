class dbToken(BasePlugin):
    def lookup(self, token):
        db = sqlite3.connect(self.source)
        db.row_factory = sqlite3.Row
        cursor = db.execute("SELECT * FROM tokens WHERE tokenstatus == 'init' AND tokenname = ?", (token,))
        row = cursor.fetchone()
        tar = None
        if row:
            db.execute("UPDATE tokens SET tokenstatus = 'used' WHERE tokenname = ?",(token,))
            db.commit()
            tar = [row['tokenip'].encode().strip(), "5900"]
        db.close()
        return tar