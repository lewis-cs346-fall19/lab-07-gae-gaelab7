import passwords
import MySQLdb
import webapp2
import random
import cgi
import cgitb
def insert_a_cookie(userid, c, conn):
    c.execute("INSERT INTO sessions(id) VALUES(%s);", (userid,))
    conn.commit()
    
def check_to_see_username(id, c, conn):
    c.execute("SELECT username FROM sessions WHERE username IS NOT NULL AND id = %s;", (id,))
    results = c.fetchall()
    if len(results) > 0:
        return results[0][0]
    else:
        return None
        
def check_the_form_for_user():
    form = cgi.FieldStorage()
    if "user" in form:
        return form.getvalue("user")
    else:
        return None
        
def username_form(self):
    self.response.write("""<html<body><form action = 'https://gwenproject.appspot.com/' method = 'get'> Enter in a username <input type=text name=user><input type =submit></form></body</html>""")
    
def update_this_user(c, conn, id, newusername):
    c.execute("UPDATE sessions SET username = %s WHERE id = %s;", (newusername, id))
    conn.commit()
    
def check_users_value(id, c, conn):
    c.execute("SELECT * FROM users WHERE id = %s;", (id,))
    conn.commit()
    results = c.fetchall()
    value = 0
    if len(results) == 0:
        c.execute("INSERT INTO users(id, value) VALUES(%s, %s);", (id,0))
        conn.commit()
        return 0
    if len(results) > 0:
        value = int(results[0][1])
        
    if check_the_form_for_increment() == id:
        c.execute('UPDATE users SET value=value+1 WHERE id=%s',(id,))
        conn.commit()
        value = value +1
    return value 
        

def increment_values(self, current_val, id):
    self.response.write("Your current value is " + str(current_val))
    self.response.write("""<html<body><form action = 'https://gwenproject.appspot.com/' method = 'get'><button type='submit' name='increment' value={}> Increment the value</button></form></body></html>""".format(id))

def check_the_form_for_increment():
    form = cgi.FieldStorage()
    if "increment" in form:
        return form.getvalue("increment")
    else:
        return None
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        conn = MySQLdb.connect(unix_socket = "/cloudsql/gwenproject:us-central1:gwensql", user = passwords.SQL_USER, passwd = passwords.SQL_PASSWD, db = "gwen")
        c = conn.cursor()
        path_info = ""
        cookie = self.request.cookies.get("cookie_name")
        if cookie == None:
            id = "%032x" % random.getrandbits(128)
            insert_a_cookie(id, c, conn)
            self.response.set_cookie("cookie_name", id, max_age=1800)
            cookie = id
        username = check_to_see_username(cookie, c, conn)
        check = check_the_form_for_user()
        if username == None and check == None:
            #getting the username from a new user
            username_form(self)
        elif username == None and check != None:
            update_this_user(c, conn, cookie, check)
            self.response.write("""<html<body>Check your<a href='https://gwenproject.appspot.com/'> VALUE</a></body</html>""")
        else:
            #adding the value
            value = check_users_value(cookie, c, conn)
            increment_values(self, value, cookie)
        
app = webapp2.WSGIApplication([("/", MainPage),], debug = True)
