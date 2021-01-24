import sys
import threading
import re
from teaches import *

def delete_test_url(conn, cursor, url):
    sql = '''
        DELETE FROM url_mapping WHERE original_url = %s
    '''
    execute_sql('delete', sql, (url), conn, cursor)


def shortened_url():
    (conn, cursor) = create_sql_conn()

    urls = [ 'https://test_{}.com'.format(i) for i in range(5) ]

    threads = []
    for url in urls:
        delete_test_url(conn, cursor, url)
        t = threading.Thread(target=get_shortened_url, args=(url,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    for url in urls:
        sql = '''
            SELECT original_url,shortened_url FROM url_mapping WHERE original_url = %s
        '''
        row = execute_sql('select', sql, (url), conn, cursor)

        if url != row['original_url']:
            return False
        if not re.search("^[a-zA-Z]{1,5}$", row['shortened_url']):
            return False

        delete_test_url(conn, cursor, url)

    close_sql_conn(conn, cursor)
    return True

def test_answer():
    assert shortened_url() == True