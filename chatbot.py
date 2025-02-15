from transformers import pipeline

# Load the model
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
chatbot = pipeline("text-generation", model=MODEL_NAME, device=0)

def chat_with_drone_bot(user_input):
    system_instruction = "You are a helpful assistant. Answer the question concisely and directly. Do not generate additional text beyond the answer."
    prompt = f"{system_instruction}\nUser: {user_input}\nBot:"
    response = chatbot(prompt, max_length=100, pad_token_id=50256)[0]["generated_text"]
    
    if "Bot:" in response:
        response = response.split("Bot:", 1)[-1].strip()
    else:
        response = response.strip()
    
    response = response.split("\n")[0]
    return response

