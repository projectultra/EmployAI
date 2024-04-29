import numpy as np
import redis
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer
import torch
from transformers import pipeline


#connect to redis database
hosting = 'local'
if hosting == "cloud":
	client = redis.Redis(
	host='redis-18541.c305.ap-south-1-1.ec2.cloud.redislabs.com',
	port=18541,
	password='') #need to add github secrets
elif hosting == "local":
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)

print(client.ping())

#read the interview questions

# model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
model_name = 'jonaschris2103/tiny_llama_embedder'
embedder = SentenceTransformer(model_name)

query = (
    Query('(*)=>[KNN 5 @question_vector $query_vector AS vector_score]')
     .sort_by('vector_score')
     .return_fields('vector_score','Question','Text')
     .dialect(2)
)

def create_query_table(query, queries, encoded_queries):
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


#change 5 to no of results and @for the the vector field name from schema

def question_answers(role=None,queries,description):
    
    encoded_queries = embedder.encode(queries)
    context_data = create_query_table(query, queries, encoded_queries)

    retrieved_data = ""
    for context in context_data:
        retrieved_data += context['Text']

    messages = [
        {
            "role": "system",
            "content": '''You are an expert hiring manager and a highly skilled job trainer.
            You have to provide the top interview questions and answers that the user may require for a job interview.
            Use the questions and answers provided in the context and tailor them to the user.''',
        },
        {
            "role": "user",
            "content": f'''Sample Interview questions: {retrieved_data}'''
        },
        {
            "role": "user",
            "content": f"Here is the Job description that you have to tailor the questions and answers to: {description}"
        }
    ]
    if role is not None:
        messages.append(
            {
                "role": "user",
                "content": f"Give me 5 interview questions {role} with the respective answer."
            }
        )
    else:
        messages.append(
            {
                "role": "user",
                "content": f"Give me 5 interview questions with the respective answer."
            }
        )

    pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")
    # We use the tokenizer's chat template to format each message - see https://huggingface.co/docs/transformers/main/en/chat_templating

    #turn generate to false to only get response
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=512, do_sample=True, temperature=0.1, top_k=50, top_p=0.95)
    
    result = outputs[0]['generated_text'].split("<|assistant|>")[1]
    
    return result

if __name__ == "__main__":
    role = "software engineer"
    queries = ['Collaboration, Communication, and Teamwork','Problem Solving and Critical Thinking','Learning and Adaptability','Work Ethic and Reliability','Leadership and Management']
    description = "Require a software engineer with 5 years of experience in Python, Java, and C++. Must have experience in developing web applications and software solutions. Must also have good communication skills and be able to work in a team."
    print(question_answers(role,queries,description))



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