import os
import json
import snowflake.connecter
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-4o-mini"

SAMPLE_N = 5

TOPICS = [
    "delivery",
    "food",
    "order",
    "payment",
    "restaurant",
    "user",
]

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
)

SYSTEM_PROMPT = f"""
You classify customer reviews for a food delivery app.

For the review you are given, return:
- sentiment_label: positive, negative, or neutral
- sentiment_score: a number between -1.0 and 1.0
- topic: one of {TOPICS}
- key_issue: a short phrase of 6 words or less that describes the main issue in the review, if any. If there is no issue, return null

Reply as JSON in this exact format:
{{
    "sentiment_label": "<sentiment_label>",
    "sentiment_score": <sentiment_score>,
    "topic": "<topic>",
    "key_issue": "<key_issue>"}}
"""

def get_connection():
    return snowflake.connecter.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
    )

def create_output_table(cursor):
    cursor.execute("CREATE SCHEMA IF NOT EXISTS ZOMATO.AI")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ZOMATO.AI.REVIEW_ENRISHED (
        REVIEW_ID STRING,
        SENTIMENT_LABEL STRING,
        SENTIMENT_SCORE FLOAT,
        TOPIC STRING,
        KEY_ISSUE STRING,
        MODEL STRING,
        ENRISHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    )
    """)

    def get_reviews_to_enrish(cursor):
        cursor.execute(f"""
            SELECT REVIEW_D, COMMENT
            FROM ZOMATO.RAW.REVIEWS
            WHERE REVIEWS_ID NOT IN (
                SELECT REVIEW_ID FROM ZOMATO.AI.REVIEW_ENRISHED
            )
            LIMIT {SAMPLE_N}
        
        """)
        return cursor.fetchall()
def classify_review(comment):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": comment},
        ],
    )
    return json.loads(response.choices[0].message.content)

def save_results(cursor,results):
    cursor.executemany(f"""
        INSERT INTO ZOMATO.AI.REVIEW_ENRISHED (
            REVIEW_ID,
            SENTIMENT_LABEL,
            SENTIMENT_SCORE,
            TOPIC,
            KEY_ISSUE,
            MODEL,
        )
        VALUES (
            %(REVIEW_ID)s,
            %(SENTIMENT_LABEL)s,
            %(SENTIMENT_SCORE)s,
            %(TOPIC)s,
            %(KEY_ISSUE)s,
            %(MODEL)s,
        )
    """, results)

def main():
    conn = get_connection()
    cursor = conn.cursor()
    create_output_table(cursor)
    reviews = get_reviews_to_enrish(cursor)

    if len(reviews) == 0:
        print("No reviews to enrich")
        return
    results = []
    for review_id, comment in reviews:
        print(f"Enriching review {review_id}")
        try:
            labels = classify_review(comment)
            print(f"labels for reviews {review_id}: {labels}")
            results.append((
                review_id,
                labels["sentiment_label"],
                labels["sentiment_score"],
                labels["topic"],
                labels["key_issue"],
                MODEL,
            ))
        except Exception as e:
            print(f"Error enriching review {review_id}: {e}")
            
    save_results(cursor,results)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
