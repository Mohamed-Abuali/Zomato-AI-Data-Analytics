from logging import PlaceHolder
from modulefinder import test
import os
from pydoc import text 
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector
from openai import OpenAI
from dotenv import load_dotenv

from zomato.ai.enrich_reviews import SYSTEM_PROMPT


load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL= "gpt-4o-mini"
NEW_REVIEWS =500
TOK_K = 5
CACHE_FILE = "reviews_embeddings.parquet"


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def read_reviews_from_snowflake():
    conn = snowflake.connector.connect(
         account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=_load_private_key(),
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )
    query = f"""
        SELECT REVIEW_ID, CITY, RATING, 
        FROM ZOMATO.STAGING.STG_REVIEWS
        SAMPLE ({NEW_REVIEWS} ROWS)
    """
    df = conn.cursor().execute(query).fetch_pandas_all()
    conn.close()

    df.columns = [col.lower() for col in df.columns]
    return df

def embed(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [items.embedding for item in response.data]

@st.cache_data()
def load_reviews():
    if os.path.exists(CACHE_FILE):
        return pd.read_parquet(CACHE_FILE)
    df = read_reviews_from_snowflake()
    df['embedding'] = embed(df['comment'].tolist())
    return df


st.title("Chat with your zomato reviews")
st.caption(f"Searching {NEW_REVIEWS} reviews, answering with {CHAT_MODEL} model")

def cosine_similarity(vec_a,vec_b):
    return np.dot(vec_a,vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def find_similar_reviews(question, df):
    question_vector = embed([question])[0]
    score = []
    for review_vector in df['embedding']:
        score.append(consine_similarity(question_vector,review_vector))
    df = df.copy()
    df['score']  = score
    return df.nlargest(TOK_K,'score')


def ask_llm(question,top_reviews):
    context = ""

    for _,row in top_reviews.itterows():
        context +=f"({row['city']},{row[rating]} stars) {row['comment']}\n"

        SYSTEM_PROMPT = (
            "Answer only using customer reviews provided. "
            "Be comncies. If the reviews don't cover it, say so"
        )
    user_prompt = f"Questions: {question}\n\nReviews:\n{context}"

    response = client.chat.completion.create(
        model=CHAT_MODEL,
        temperature= 0.8,
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":user_prompt}
        ]
    )
    return response.choices[0].message.content

review_df =load_reviews()

question = st.text_input(
    "Ask a question about your reviews:",
    placeholder="e.g. What are the most common complaints about delivery?"
)
if question:
    top_reviews = find_similar_reviews(question,review_df)
    answer = ask_llm(question,top_reviews)

    st.markdown(f"**Answer:**")
    st.write(answer)
    with st.expander("Reviews used to build this answer"):
        st.dataframe(top_reviews[['city','rating','comment']],hide_index=True)