from ollama import chat

print("Start")

response = chat(
    model='phi3:mini',
    messages=[
        {
            'role': 'user',
            'content': 'hello'
        }
    ]
)

print(response)
print("Done")