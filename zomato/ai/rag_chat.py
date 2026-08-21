from modulefinder import test
import os
from pydoc import text 
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector
from openai import OpenAI
from dotenv import load_dotenv


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




