import json
import time

import numpy as np
import pandas as pd

import redis
import requests
from redis.commands.search.field import (
    NumericField,
    TagField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

#connect to redis database
hosting = 'cloud'
if hosting == "cloud":
    client = redis.Redis(
    host='redis-16071.c264.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=16071,
    password='iuz2JyKXJ2kqZ0xwKS1puMu4wr7khhVi') #need to add github secrets

print(client.ping())

if True:
    df = pd.read_csv("df.csv")
    df.dropna(inplace=True)
    print(df.head())
    pipeline = client.pipeline()
    for index, row in df.iterrows():
        redis_key = f"{row['Type']}:{index:03}"
        text = row['Question'] + " " + row['Answer']
        data = {'Question': row['Question'],'Text': text}
        json_text = json.dumps(data)
        pipeline.json().set(redis_key, "$", json.loads(json_text))

    print(pipeline.execute())

print(client.json().get("Common:000","$.Text"))

keys = sorted(client.keys("Common:*"))
questions = client.json().mget(keys, "$.Question")
questions = [item for sublist in questions for item in sublist]
fulltext = client.json().mget(keys, "$.Text")
fulltext = [item for sublist in fulltext for item in sublist]


# model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

model_name = "jonaschris2103/tiny_llama_embedder"
embedder = SentenceTransformer(model_name)

# embedder.push_to_hub("tiny_llama_embedder")

question_embeddings = embedder.encode(questions).astype(np.float32).tolist()
text_embeddings = embedder.encode(fulltext).astype(np.float32).tolist()
VECTOR_DIMENSION = len(question_embeddings[0])
print(VECTOR_DIMENSION) #expected 2048 for tinyllama



pipeline = client.pipeline()
for key, question_embedding, text_embedding in zip(keys, question_embeddings,text_embeddings):
    pipeline.json().set(key, "$.question_embeddings", question_embedding)
    pipeline.json().set(key, "$.text_embeddings", text_embedding)

print(pipeline.execute())

print(client.json().get("Common:010"))

schema = (
    TextField("$.Question", no_stem=True, as_name="Question"),
    TextField("$.Text", no_stem=True, as_name="Text"),
    VectorField(
        "$.question_embeddings",
        "FLAT",
        {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIMENSION,
            "DISTANCE_METRIC": "COSINE",
        },
        as_name="question_vector",
    ),
    VectorField(
        "$.text_embeddings",
        "FLAT",
        {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIMENSION,
            "DISTANCE_METRIC": "COSINE",
        },
        as_name="text_vector",
    ),
)

if False:
    definition = IndexDefinition(prefix=["Common:"], index_type=IndexType.JSON)
    res = client.ft("idx:double_vectors").create_index(
        fields=schema, definition=definition)
    print(res)

    info = client.ft("idx:double_vectors").info()
    num_docs = info["num_docs"]
    indexing_failures = info["hash_indexing_failures"]
    print(f"{num_docs} documents indexed with {indexing_failures} failures")


query = (
    Query('(*)=>[KNN 5 @question_vector $query_vector AS vector_score]')
     .sort_by('vector_score')
     .return_fields('vector_score','Question','Text')
     .dialect(2)
)



def create_query_table(query, queries, encoded_queries, extra_params={}):
    results_list = []
    for i, encoded_query in enumerate(encoded_queries):
        result_docs = (
            client.ft("idx:double_vectors")
            .search(
                query,
                {
                    "query_vector": np.array(
                        encoded_query, dtype=np.float32
                    ).tobytes()
                }
                | extra_params,
            )
            .docs
        )
        for doc in result_docs:
            vector_score = round(1 - float(doc.vector_score), 2)
            results_list.append(
                {
                    "query": queries[i],
                    "Text": doc.Text,
                    "score": vector_score,
                    "id": doc.id,
                }
            )
    return results_list

queries = [
    "Questions on projects, teamwork, collaboration, communication ",
]
encoded_queries = embedder.encode(queries)
create_query_table(query, queries, encoded_queries)

context = '''
1 Question: How do you handle challenging situations or conflicts within a team? Answer: I approach challenging situations by (describe your approach, e.g., staying calm and seeking collaborative solutions). In a previous project at (previous company), I successfully resolved a conflict by (provide a brief example), emphasizing open communication and finding common ground.
2 Question: How do you handle competing priorities and multiple projects simultaneously? Answer: I handle competing priorities by (mention your approach, e.g., setting clear priorities, multitasking efficiently). Utilizing time management skills and regularly reassessing priorities help me navigate and successfully manage multiple projects concurrently.
3 Question: How do you handle situations where your team is not meeting its goals? Answer: Addressing a team not meeting its goals involves (mention your approach, e.g., identifying root causes, collaborating on solutions). I addressed a similar situation by (describe your actions, e.g., analyzing performance metrics, implementing targeted training).
4 Question: How do you contribute to fostering a collaborative team environment? Answer: I contribute to a collaborative team environment by (mention your actions, e.g., promoting open communication, encouraging diverse perspectives). Building a positive and inclusive atmosphere is essential for achieving collective goals.
5 Question: How do you foster a culture of continuous improvement within your team? Answer: Fostering a culture of continuous improvement involves (mention your strategies, e.g., encouraging feedback, promoting a growth mindset). I fostered such a culture in a previous team by (describe your specific actions, e.g., implementing regular retrospectives, celebrating small wins).
'''

import torch
from transformers import pipeline
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

# We use the tokenizer's chat template to format each message - see https://huggingface.co/docs/transformers/main/en/chat_templating

role = None

messages = [
    {
        "role": "system",
        "content": '''You are an expert hiring manager and a highly skilled job trainer.
        You have to provide the top interview questions and answers that the user may require for a job interview.
        Use the questions and answers provided in the context and tailor them to the user.''',
    },
    {
        "role": "user",
        "content": f'''Context: {context}'''
    },
    {
        "role": "user",
        "content": f"Give me 5 interview questions {role}with answers."
    }
]
prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, max_new_tokens=512, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
print(outputs[0]["generated_text"])

# API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# headers = {"Authorization": "Bearer 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"}


#redis password
#iuz2JyKXJ2kqZ0xwKS1puMu4wr7khhVi


# def query(payload):
# 	response = requests.post(API_URL, headers=headers, json=payload)
# 	return response.json()
	
# output = query({
# 	"inputs": "Here are 5 interview questions for a software engineering role with answers",
#  "return_full_text":True
# })

# print(output)
