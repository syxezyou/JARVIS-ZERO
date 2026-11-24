import os, sqlite3, threading, secrets, re
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from core import NeuralRanker
from search import search_web

ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
Path('data').mkdir(exist_ok=True)
DB='data/jarvis.sqlite3'
LOCK=threading.Lock()
RANKER=NeuralRanker()
app=FastAPI(title='J.A.R.V.I.S. ZERO')

def db():
    c=sqlite3.connect(DB, timeout=10)
    c.row_factory=sqlite3.Row
    return c

with db() as c:
    c.execute('CREATE TABLE IF NOT EXISTS exchanges(id INTEGER PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS corrections(id INTEGER PRIMARY KEY, question TEXT NOT NULL, correction TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')

def auth(authorization):
    token=os.getenv('JARVIS_TOKEN','')
    if not token or not secrets.compare_digest(authorization or '', 'Bearer '+token):
        raise HTTPException(401, 'Token invalide')

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=600)
class Feedback(BaseModel):
    question: str = Field(min_length=3, max_length=600)
    correction: str = Field(min_length=3, max_length=2000)

@app.get('/')
def index(): return FileResponse('static/index.html')

@app.post('/api/ask')
def ask(payload:Ask, authorization:str|None=Header(default=None)):
    auth(authorization)
    question=payload.question.strip()
    with LOCK:
        with db() as c:
            matches=c.execute('SELECT question,correction FROM corrections ORDER BY id DESC LIMIT 100').fetchall()
    # Always research BEFORE answering, even when memory contains an earlier correction.
    try:
        sources=search_web(question)
    except Exception as e:
        return {'answer':'Recherche Internet indisponible. Je ne peux pas fournir de réponse sourcée pour le moment.', 'sources':[], 'status':'search_unavailable', 'detail':type(e).__name__}
    if not sources:
        return {'answer':'Aucune source exploitable trouvée. Je préfère ne pas inventer de réponse.', 'sources':[], 'status':'no_sources'}
    with LOCK:
        ranked=sorted(sources, key=lambda s:RANKER.score(question,s['title']+' '+s['snippet']), reverse=True)[:4]
    # Extractive, attributed synthesis: avoids pretending a tiny randomly initialized net can generate reliable prose.
    lines=['Voici ce que les résultats de recherche indiquent (extraits non vérifiés indépendamment) :']
    for i,s in enumerate(ranked,1):
        lines.append(f'[{i}] {s["title"]} — {s["snippet"]}')
    if matches:
        import difflib
        best=max(matches,key=lambda m:difflib.SequenceMatcher(None,question.lower(),m['question'].lower()).ratio())
        if difflib.SequenceMatcher(None,question.lower(),best['question'].lower()).ratio() >= .86:
            lines.append('Mémoire (correction utilisateur non vérifiée) : '+best['correction'])
    answer='\n\n'.join(lines)
    with LOCK:
        with db() as c: c.execute('INSERT INTO exchanges(question,answer) VALUES (?,?)',(question,answer))
    return {'answer':answer,'sources':[{'id':i,**s} for i,s in enumerate(ranked,1)],'status':'ok'}

@app.post('/api/feedback')
def feedback(payload:Feedback,authorization:str|None=Header(default=None)):
    auth(authorization)
    with LOCK:
        with db() as c:
            c.execute('INSERT INTO corrections(question,correction) VALUES (?,?)',(payload.question,payload.correction))
        RANKER.train(payload.question,payload.correction,True)
    return {'saved':True,'note':'Correction mémorisée ; le réseau neuronal de classement a reçu un exemple positif, sans garantie de justesse.'}

@app.get('/api/health')
def health(): return {'status':'ok','model':'random-initialized neural source ranker','internet':'SearXNG'}
