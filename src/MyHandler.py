import time
import BaseHTTPServer
import urllib
import MySQLdb

HOST_NAME = 'localhost'
PORT_NUMBER = 8080 # Maybe set this to 9000.

db_name = 'testdb'
db_host = '127.0.0.1'
db_user = 'test'
db_pass = 'test'
db_table = 'bm_three_code'

CONTENT_TYPE = {'html': 'text/html',
                'css': 'text/css',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'js': 'application/x-javascript',
                'gif': 'image/gif'}

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(s):
    path = s.path
    if(path.startswith('/html') == 1):
      filepath = '/'.join(path.split('/')[1:])
      s._getFile(filepath)
      return
    
    """Respond to a GET request."""
    prefix = s._getQueryPrefix()
    json = s._testdb(prefix)
    s.send_response(200)
    s.send_header("Content-type", "application/json;charset=utf-8")
    s.send_header("Content-Length", len(json))
    s.end_headers()
    s.wfile.write(json)
  def _getFile(s, path):
    try:
      file = open(path)
      fcontent = file.read()
      file.close()
      pos = path.rfind('.')
      type = 'html'
      if(pos != -1):
        type = path.split('.')[-1]
      if(type != 'html' and type != 'css' and type != 'js'):
        return
      s.send_response(200)
      s.send_header("Content-type", CONTENT_TYPE[type])
      s.end_headers()
      s.wfile.write(fcontent)
    except IOError:
      pass
  def _getQueryPrefix(s):
    return urllib.unquote(s.path.replace("/",""))
  def _testdb(s, prefix):
    conn = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name, use_unicode=True)
    cursor = conn.cursor()
    if(len(prefix) == 0):
      cursor.execute("""select ID, AIRPORT_THREE_CODE, AIRPORT_ENGLISH_NAME from bm_three_code
        where COUNTRY_CODE = %s and AIRPORT_ENGLISH_NAME is not null order by AIRPORT_THREE_CODE asc limit 0, 12""", ('CHN',))
    else:
      cursor.execute("""select ID, AIRPORT_THREE_CODE, AIRPORT_ENGLISH_NAME from bm_three_code
        where (AIRPORT_THREE_CODE like %s or AIRPORT_ENGLISH_NAME like %s) and AIRPORT_ENGLISH_NAME is not null order by AIRPORT_THREE_CODE asc""", (prefix + '%', prefix + '%'))
    rows = cursor.fetchall()
    li = []
    for row in rows:
      li.append(','.join(['{"cityEngName":"' + row[2] + '"', '"code":"' + row[1] + '"}']))
    body = ','.join(li)
    json = ''.join(['{"airports":[', body, ']}'])
    cursor.close()
    conn.close()
    return json

if __name__ == '__main__':
  server_class = BaseHTTPServer.HTTPServer
  httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
  print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    pass
  httpd.server_close()
  print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
