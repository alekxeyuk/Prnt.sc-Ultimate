import requests
from random import choice
import string
import sys
from bs4 import BeautifulSoup as BSHTML
from tinydb import TinyDB, Query
import threading


def GenRandomLine(length=5, chars=string.ascii_lowercase + string.digits):
    return ''.join([choice(chars) for i in range(length)])

def dl_im(session, id):
    complete = False
    alive = True
    try:
        with print_lock:
            if db.search(User.id == id):
                raise Exception("Already downloaded")
        r = session.get('https://prnt.sc/{id}'.format(id=id))
        alive = True
        if r.status_code == 403 or "Attention Required" in r.text:
            return ""
        if r.status_code == 503:
            dl_im(session, id)
            complete = False
            alive = False
            return ""
        if '0_173a7b_211be8ff.png' not in r.text:
            soup = BSHTML(r.text, "lxml")
            link = soup.findAll('img')[0]['src']
            with open(folder + '/' + link.split('/')[-1], 'wb') as f:
                r = session.get(link, stream=True)
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print("[ + ] Image {id} found".format(id=id))
            with print_lock:
                db.insert({'id': id})
        else:
            print("[ - ] Image {id} is not present".format(id=id))
        complete = True
    except Exception as e:
        print("[ ! ] {id} dropped error = {e}".format(id=id, e=e))
    finally:
        if complete or alive:
            semaphore.release()

if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.exit("Usage: python " + sys.argv[0] + " (Number of threads) (db.json file-name) (safe folder) (prefix) (lenght : 4 or 5)")
    num_threads, db_name, folder, prefix, lenght = sys.argv[1:]
    
    semaphore = threading.BoundedSemaphore(value=int(num_threads))
    print_lock = threading.Lock()
    
    db = TinyDB(db_name)
    User = Query()
    
    s = requests.Session()
    s.proxies.update({'http': 'http://{}'.format("127.0.0.1:8888"),'https': 'https://{}'.format('127.0.0.1:8888')})
    s.headers.update({"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36", "cookie": "__cfduid=d59075350144398074a7d392923cd54b"+GenRandomLine(len("71544493780")), "referer": "https://prnt.sc/l486oi", 'x-powered-by': 'Magic'})
    while True:
        semaphore.acquire()
        t = threading.Thread(target=dl_im, args=(s,'{0}{1}'.format(prefix, GenRandomLine(int(lenght))), ))
        t.start()