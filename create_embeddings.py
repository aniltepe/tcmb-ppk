import os
import json
import re
from datetime import datetime

import nltk
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize, word_tokenize, PunktTokenizer
from gensim.models import Word2Vec


json_data = []
for path, dirs, files in os.walk(f"./output"):
    for file in files:
        if file.endswith(".json"):
            f = open(os.path.join(path, file), encoding="utf-8-sig")
            json_data.append(json.load(f))
            f.close()
print("number of documents:", len(json_data))


sw_file = open('./stopwords.txt')
stop_words = sw_file.read()
stop_words = stop_words.split("\n")
sw_file.close()
print("stop words count:", len(stop_words))

text_data = [f"{' '.join([i['text'] for topic in j['topics'] for i in topic['items']])} {j['abstract']}" for j in json_data]

regexes = [
    (r"([’’])", "'"),
    (r"([“”\"])", ""),
    (r"â", "a"),
    (r"î", "i"),
    (r"û", "u"),
    (r"Â", "A"),
    (r"Î", "İ"),
    (r"Û", "U"),
]

text_clean = text_data
for reg in regexes:
    text_clean = [re.sub(reg[0], reg[1], t) for t in text_clean]

text_lower = [t.replace("İ", "i").replace("I", "ı").lower() for t in text_clean]

text_lower = [" ".join([word for word in sent.split(" ") if word not in stop_words]) for sent in text_lower]

regexes2 = [
    (r"(,\s)", " "),
    (r"([\.;\(\)])", ""), 
    (r"['\-]", " "),
]

for reg in regexes2:
    text_lower = [re.sub(reg[0], reg[1], t) for t in text_lower]

text_lower = [" ".join([word for word in sent.split(" ") if word not in stop_words and word != ""]) for sent in text_lower]

data = [word_tokenize(t, "turkish") for t in sent_tokenize(" ".join(text_lower), "turkish")]
print("word token count:", len(data[0]))

vector_size, window, epochs = 500, 20, 100
print("word2vec model is being trained", f"vector_size={vector_size} window={window}, epochs={epochs}")
model = Word2Vec(data, vector_size=vector_size, window=window, epochs=epochs)

timestamp = datetime.now().strftime("%y%m%d%H%M")
model.save(f"word2vec_{timestamp}.model")
model.wv.save(f"word2vec_{timestamp}.vectors")
print("word2vec model checkpoint and keyed vectors have been saved", f"word2vec_{timestamp}")