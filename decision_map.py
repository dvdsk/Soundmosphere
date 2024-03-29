import time
import random
import threading
import sqlite3

from queue import Queue as tQueue

from text_analysis import analyseText
from music_player import play, Order, OrderType

MAX_RECENT_WORDS = 90
MIN_ENG_DIFF = 0.1
MIN_STRESS_DIFF = 0.1
LIMIT = 10

def analyse(rx, playlist_changes):
    t = threading.currentThread()
    recent_words = []

    db_path = "database.sqlite"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    energylast = -1
    stresslast = -1
    pathlast = ""

    while getattr(t, "keep_running", True):
        if not rx.poll(timeout=0.1):
            continue
        
        new_text = rx.recv()
        recent_words = recent_words+new_text.split(" ")
        recent_words = recent_words[-MAX_RECENT_WORDS:]
        recent_text = " ".join(recent_words)
        print(new_text)

        energy, stress = analyseText(recent_text)
        print("energy: ", energy, " stress:",stress)

        if (abs(energylast - energy) > MIN_ENG_DIFF or abs(stresslast - stress) > MIN_STRESS_DIFF):
          q = "SELECT path FROM features ORDER BY ABS(energy+{})+ABS(stress+{}) ASC LIMIT {};".format(energy,stress,LIMIT)  
          paths = list(c.execute(q))
          rand = int(random.random()*len(paths))
          if paths:
            path = paths[rand]
            if (pathlast != path):
              order = Order()
              order.path = path[0]
              playlist_changes.put(order)

              energylast = energy
              stresslast = stress
              pathlast = path
          
          time.sleep(5)

    print("stopped analysis")

"""
import spacy
nlp = spacy.load("data/en_core_web_sm")

def linguistic_analysis(recent_text):
    doc = nlp(recent_text)



def find_subject(doc):
    root = [token for token in doc if token.head == token][0]
    subject = list(root.lefts)[0]
    return subject

if __name__ == '__main__':

    short_subject = "Smaug shot spouting into the air, turned over and crashed down from on high in ruin."
    long_subject = "Smaug shot spouting into the air, turned over and crashed down from on high in ruin. Full on the town he fell. His last throes splintered it to sparks and gledes"    
    long_calm = "They made north-west, slanting away from te River Running, and drawing ever nearer and nearer to a great spur of the Mountain that was flung out southwards towards them."
    test = "while lisa killed the dragon she was slain"

    keywords = ["crashed", "killed"]

    #iterate through tree until word found that is in list of interesting words
    #ascend up till the parent/subject. Determine if subject is friendly or hostile

    #TODO
    #sentiment	float	A scalar value indicating the positivity or negativity of the token.

    doc = nlp(test)
    for token in doc:
        if token.text in keywords:
            subject = find_subject(doc)
            print(subject)

    print(doc)
    print(spacy.explain("VBG"))


    print("stopped analysis")
"""