import os 
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