import sys,os,time
from flask import Flask,request,render_template,redirect
from flask_caching import Cache
from linkpreview import link_preview
import validators
import pymysql.cursors
import json,string
import httplib2

URL_PREFIX = 'http://127.0.0.1:5000/'
RETRY = 3
REQUEST_TIMEOUT = 5

letters = list(string.ascii_lowercase)
letters.extend(list(string.ascii_uppercase))
DIGIT_MAPPING = {  i:l for i,l in enumerate(letters) }

config = {
    "DEBUG": True,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 60
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

def create_sql_conn():
    try:
        with open('cred.json') as json_file:
            cred = json.load(json_file)
        conn = pymysql.connect(host=cred['ip'], port=cred['port'], user=cred['username'], passwd=cred['password'], db=cred['database'], charset="utf8")
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        return (conn, cursor)
    except:
        sys.exit("Error: unable to create database connection.")


def close_sql_conn(conn, cursor):
    cursor.close()
    conn.close()

def execute_sql(action, sql, parameters, conn=None, cursor=None):
    try:
        res = cursor.execute(sql, parameters)
        if action != 'select':
            conn.commit()
        else:
            res = cursor.fetchone()
        return res
    except:
        close_sql_conn(conn, cursor)
        sys.exit("Error: unable to {} data.".format(action))


def lock(timestamp, lock=True, conn=None, cursor=None):
    release_lock = not lock

    sql = '''
        UPDATE `lock` SET timestamp = %s WHERE id = 1 AND timestamp = %s
    '''
    return execute_sql('update', sql, (0 if release_lock else timestamp, timestamp if release_lock else 0), conn, cursor)


def is_available(url):
    counter = 0
    while counter < RETRY:
        counter += 1
        try:
            h = httplib2.Http()
            resp = h.request(url, 'HEAD')
            if int(resp[0]['status']) < 400:
                return True
            else:
                return False
        except:
            time.sleep(0.5)

    return False


def get_shortened_url(original_url):
    (conn, cursor) = create_sql_conn()

    sql = '''
        SELECT shortened_url FROM url_mapping WHERE original_url = %s
    '''
    shortened_url = execute_sql('select', sql, (original_url), conn, cursor)
    if shortened_url:
        close_sql_conn(conn, cursor)
        return shortened_url['shortened_url']

    t = time.time()
    while lock(timestamp=t, lock=True, conn=conn, cursor=cursor) == 0:
        time.sleep(0.05)

    sql = '''
        SELECT COUNT(*) counter
        FROM url_mapping
    '''
    counter = execute_sql('select', sql, (), conn, cursor)
    counter = counter['counter']

    num = counter + 1
    remainder_list = []
    while num > 0:
        remainder_list.append(DIGIT_MAPPING[num%52])
        num = int(num/52)
    shortened_url = ''.join(remainder_list[::-1])

    sql = '''
        INSERT INTO url_mapping (original_url, shortened_url) VALUES (%s, %s)
    '''
    execute_sql('insert', sql, (original_url, shortened_url), conn, cursor)

    while lock(timestamp=t, lock=False, conn=conn, cursor=cursor) == 0:
        time.sleep(0.05)    
    close_sql_conn(conn, cursor)

    return shortened_url


def get_preview(url):
    try:
        preview = link_preview(url)
    except:
        return { 'error': 'no preview available' }
    return { 'title': preview.title, 'image': preview.absolute_image }


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.values['url']
        if not validators.url(original_url):
            return render_template('index.html', valid_url=False, original_url=original_url)
        
        return render_template('index.html', valid_url=True, original_url=original_url, shortened_url="{}{}".format(URL_PREFIX, get_shortened_url(original_url)), preview=get_preview(original_url), is_available=is_available(original_url))

    return render_template('index.html')


@app.route('/<shortened_url>', methods=['GET'])
def redirect_url(shortened_url):
    (conn, cursor) = create_sql_conn()

    sql = '''
        SELECT original_url FROM url_mapping WHERE shortened_url = %s
    '''
    original_url = execute_sql('select', sql, (shortened_url), conn, cursor)

    close_sql_conn(conn, cursor)

    if original_url:
        return redirect(original_url['original_url'], code=302)
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')