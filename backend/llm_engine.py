from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

def generate_answer(context, question):
    prompt = f"""
    You must answer the question ONLY using the context below.
    Do NOT add anything extra.
    If answer is in context, return EXACT meaning.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = model.generate(
        **inputs,
        max_length=250,
        temperature=0.1
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

