from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()
origins = ["http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Вы можете ограничить источники для большей безопасности
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Comment(BaseModel):
    post_id: int
    author: str
    comment: str

class Post(BaseModel):
    id: int
    title: str
    content: str
    comments: list[Comment] = []

def get_db_connection():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/posts")
async def get_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    results = []
    for post in posts:
        post_dict = dict(post)
        post_dict['comments'] = [dict(comment) for comment in conn.execute('SELECT * FROM comments WHERE post_id = ?', (post['id'],)).fetchall()]
        results.append(post_dict)
    conn.close()
    return results

@app.get("/api/posts/{post_id}/comments")
async def get_comments(post_id: int):
    conn = get_db_connection()
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,)).fetchall()
    conn.close()
    return [dict(comment) for comment in comments]

@app.post("/api/posts/{post_id}/comments")
async def add_comment(post_id: int, comment: Comment):
    conn = get_db_connection()
    conn.execute('INSERT INTO comments (post_id, author, comment) VALUES (?, ?, ?)',
                 (post_id, comment.author, comment.comment))
    conn.commit()
    conn.close()
    return {"message": "Comment added successfully"}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Blog API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

