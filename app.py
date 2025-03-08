import streamlit as st
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

# Initialize Hugging Face token
def get_huggingface_token():
    """Get Hugging Face token from secrets.toml"""
    try:
        if 'HUGGINGFACE_API_TOKEN' not in st.secrets:
            st.error("""
            ⚠️ Hugging Face API token not found! Please follow these steps:
            1. Create a file named '.streamlit/secrets.toml'
            2. Add your token as: HUGGINGFACE_API_TOKEN = "your_token_here"
            3. Get your token from: https://huggingface.co/settings/tokens
            """)
            st.stop()
        return st.secrets['HUGGINGFACE_API_TOKEN']
    except Exception:
        st.error("""
        ⚠️ Could not load secrets.toml file. Please create it in the .streamlit folder.
        Add your Hugging Face API token as: HUGGINGFACE_API_TOKEN = "your_token_here"
        """)
        st.stop()

hf_token = get_huggingface_token()

# Model selection and parameters
model_map = {
    'Llama 3.1 (70B)': "meta-llama/Llama-3.1-70B-Instruct",
    'Llama 3.2 (70B)': "meta-llama/Llama-3.2-70B-Instruct",
    'Llama 3.3 (70B)': "meta-llama/Llama-3.3-70B-Instruct",
    'Llama 2 (7B)': "meta-llama/Llama-2-7b-chat-hf",
    'Llama 2 (13B)': "meta-llama/Llama-2-13b-chat-hf",
    'Llama 2 (70B)': "meta-llama/Llama-2-70b-chat-hf",
    'Mistral 7B': "mistralai/Mistral-7B-Instruct-v0.1",
    'Mistral Mixtral-8x7B': "mistralai/Mixtral-8x7B-Instruct-v0.1",
    'Mistral 13B': "mistralai/Mistral-13B-Instruct-v0.1",
    'GPT-2': "gpt2",
    'GPT-Neo': "EleutherAI/gpt-neo-1.3B",
}

# Organize models by category
models_by_category = {
    '🦙 Llama 3 Models': ['Llama 3.1 (70B)', 'Llama 3.2 (70B)', 'Llama 3.3 (70B)'],
    '🦙 Llama 2 Models': ['Llama 2 (7B)', 'Llama 2 (13B)', 'Llama 2 (70B)'],
    '🔮 Mistral Models': ['Mistral 7B', 'Mistral Mixtral-8x7B', 'Mistral 13B'],
    '🤖 GPT Models': ['GPT-2', 'GPT-Neo']
}

# Default model settings
default_category = '🔮 Mistral Models'
default_model = 'Mistral Mixtral-8x7B'

# Page config
st.set_page_config(
    page_title="✨ PINK AI",
    page_icon="🎀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with animations and chat bubbles
st.markdown("""
<style>
    .main .block-container {
        background: linear-gradient(135deg, #FFF0F5, #FFE4E1);
        padding: 2rem;
        border-radius: 20px;
    }
    
    /* Title and floating emojis */
    .title-container {
        position: relative;
        text-align: center;
        padding: 40px 0;
        margin: 20px 0;
        min-height: 200px;
    }
    
    .emoji {
        position: absolute;
        font-size: 24px;
        opacity: 0.8 ;
        animation: float 3s ease-in-out infinite;
        z-index: 1;
    }
    
    /* Position each emoji */
    .emoji-1 { left: 10%; top: 20%; animation-delay: 0s; }
    .emoji-2 { left: 20%; top: 40%; animation-delay: 0.3s; }
    .emoji-3 { left: 26%; top: 60%; animation-delay: 0.6s; }
    .emoji-4 { left: 40%; top: 85%; animation-delay: 0.9s; }
    .emoji-5 { left: 50%; top: 13%; animation-delay: 1.2s; }
    .emoji-6 { left: 64%; top: 22%; animation-delay: 1.5s; }
    .emoji-7 { left: 70%; top: 60%; animation-delay: 1.8s; }
    .emoji-8 { left: 80%; top: 80%; animation-delay: 2.1s; }
    .emoji-9 { left: 87%; top: 20%; animation-delay: 2.4s; }
    .emoji-10 { left: 15%; top: 70%; animation-delay: 2.7s; }
    .emoji-11 { left: 27%; top: 20%; animation-delay: 3s; }
    .emoji-12 { left: 35%; top: 10%; animation-delay: 3.3s; }
    .emoji-13 { left: 53%; top: 80%; animation-delay: 3.6s; }
    .emoji-14 { left: 72%; top: 15%; animation-delay: 3.9s; }
    .emoji-15 { left: 62%; top: 75%; animation-delay: 4.2s; }
    .emoji-16 { left: 77%; top: 46%; animation-delay: 4.5s; }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0) rotate(0deg);
        }
        50% {
            transform: translateY(-20px) rotate(10deg);
        }
    }
    
    /* Title styling */
    .main-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(120deg, #FF69B4, #FF1493);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(255, 105, 180, 0.3);
        position: relative;
        z-index: 10;
        letter-spacing: 1px;
    }
    
    .subtitle {
        color: #FF69B4;
        font-size: 1.2rem;
        margin-top: 10px;
        position: relative;
        z-index: 10;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        z-index: 20;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
    }
    
    .stChatMessage[data-testid="user-chat-message"] {
        background: linear-gradient(135deg, rgba(255, 240, 245, 0.9), rgba(255, 228, 225, 0.9));
        border-radius: 20px 20px 5px 20px;
        margin-left: 40px;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.2);
    }
    
    .stChatMessage[data-testid="assistant-chat-message"] {
        background: linear-gradient(135deg, rgba(255, 192, 203, 0.8), rgba(255, 182, 193, 0.8));
        border-radius: 20px 20px 20px 5px;
        margin-right: 40px;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.2);
    }
    
    .stChatMessage .stAvatar {
        display: none !important;
    }
    
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 25px;
        padding: 5px 15px;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.2);
        position: relative;
        z-index: 20;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 192, 203, 0.2);
        position: relative;
        z-index: 20;
    }
    
    /* Ribbon emoji animation */
    .ribbon-emoji {
        display: inline-block;
        animation: sparkle 2s ease-in-out infinite;
    }
    
    @keyframes sparkle {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
</style>

<div class='title-container'>
    <span class='emoji emoji-1'>🦩</span>
    <span class='emoji emoji-2'>🦢</span>
    <span class='emoji emoji-3'>🩷</span>
    <span class='emoji emoji-4'>🌸</span>
    <span class='emoji emoji-5'>💗</span>
    <span class='emoji emoji-6'>🌷</span>
    <span class='emoji emoji-7'>🐇</span>
    <span class='emoji emoji-8'>🤍</span>
    <span class='emoji emoji-9'>🎀</span>
    <span class='emoji emoji-10'>🧸</span>
    <span class='emoji emoji-11'>🍭</span>
    <span class='emoji emoji-12'>🫧</span>
    <span class='emoji emoji-13'>🧁</span>
    <span class='emoji emoji-14'>🦢</span>
    <span class='emoji emoji-15'>🍒</span>
    <span class='emoji emoji-16'>🍓</span>
    <div class='main-title'>PINK AI</div>
    <p class='subtitle'>Your <i>pinky</i> AI companion ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with ribbon emojis
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2 style='margin-bottom: 20px; color: #FF1493;'>
                <span class='ribbon-emoji'>🎀</span>
                rey-dal
                <span class='ribbon-emoji'>🎀</span>
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Model selection and parameters
    st.markdown("""
        <div style='background: linear-gradient(135deg, #FFE4E1, #FFF0F5); padding: 15px; border-radius: 15px; margin: 10px 0;'>
            <h3 style='text-align: center; margin: 0; color: #FF1493;'>Model Settings</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Model category selection
    model_category = st.selectbox(
        'Select Category:',
        list(models_by_category.keys()),
        index=list(models_by_category.keys()).index(default_category)
    )

    # Model selection within category
    available_models = models_by_category[model_category]
    default_index = available_models.index(default_model) if default_model in available_models else 0
    
    model_name = st.selectbox(
        'Choose Model:',
        available_models,
        index=default_index
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Add info about model access
    if any(name in model_map[model_name].lower() for name in ["llama-3", "llama-2"]) or 'Llama' in model_category:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #FFE4E1, #FFF0F5); padding: 15px; border-radius: 15px; border: 2px solid #FF69B4; margin: 10px 0;'>
                <p style='color: #FF1493; margin: 0; font-size: 16px;'>
                    🎀 <b>Quick note!</b> You'll need access to use this model.
                    <br><br>
                    Visit <a href='https://huggingface.co/meta-llama' style='color: #FF69B4;'>huggingface.co/meta-llama</a> to get started! 💝
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Parameters section with decorative header
    st.markdown("""
        <div style='background: linear-gradient(135deg, #FFE4E1, #FFF0F5); padding: 15px; border-radius: 15px; margin: 10px 0;'>
            <h3 style='text-align: center; margin: 0; color: #FF1493;'>Parameters</h3>
        </div>
    """, unsafe_allow_html=True)
    
    do_sample = st.checkbox('Enable sampling', value=True, help='When disabled, uses greedy decoding (always picks most likely token)')
    
    temperature = st.slider(
        'Temperature:', 
        min_value=0.0, 
        max_value=2.0,
        value=0.1,
        step=0.1,
        help='Higher values make the output more random, lower values make it more focused and deterministic'
    )

    top_p = st.slider(
        'Top P (nucleus sampling):', 
        min_value=0.0, 
        max_value=1.0,
        value=0.95,
        step=0.05,
        help='Controls diversity via nucleus sampling: 0.9 means consider the top 90% most likely tokens'
    )

    top_k = st.slider(
        'Top K:', 
        min_value=0, 
        max_value=100,
        value=40,
        step=5,
        help='Limits the number of tokens to consider for each step of text generation'
    )

    max_length = st.slider(
        'Max Length:', 
        min_value=64,
        max_value=1024 if "gpt" in model_map[model_name].lower() else 4096,
        value=512 if "gpt" in model_map[model_name].lower() else 2048,
        step=64,
        help='Maximum length of generated text'
    )

    repetition_penalty = st.slider(
        'Repetition Penalty:', 
        min_value=1.0,
        max_value=2.0,
        value=1.2,
        step=0.1,
        help='Higher values penalize repetition more strongly'
    )

    # Clear chat button with updated rerun
    if st.sidebar.button("Clear Chat 🗑️"):
        st.session_state.messages = [{"role": "assistant", "content": "✨ Hi there! I'm your AI assistant. How can I help you today? 🌸"}]
        st.rerun()

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "✨ Hi there! I'm your AI assistant. How can I help you today? 🌸"}]

def generate_llama_response(prompt_input, string_dialogue):
    try:
        model_id = model_map[model_name]
        client = InferenceClient(model=model_id, token=hf_token)
        
        # Model parameters from memory
        parameters = {
            "max_new_tokens": 512 if "gpt" in model_id.lower() else max_length,  # Lower for GPT models
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repetition_penalty": repetition_penalty
        }
        
        # Create a more engaging system prompt
        system_prompt = """You are a friendly and helpful AI assistant with a warm personality. You should:
1. Be engaging and conversational while remaining professional
2. Show empathy and understanding in your responses
3. Give detailed and helpful answers
4. Use appropriate emojis to make the conversation more lively
5. Avoid saying you don't have feelings or that you're an AI - just be helpful and friendly
"""
        
        # For chat models, include dialogue history
        if any(name in model_id.lower() for name in ["llama", "mistral"]):
            full_prompt = f"{string_dialogue} {prompt_input} Assistant: "
        else:
            full_prompt = prompt_input
            
        response = client.text_generation(
            system_prompt + full_prompt,
            **parameters
        )
        
        return response
        
    except Exception as e:
        if "401 Client Error" in str(e):
            return "⚠️ Invalid API token. Please check your HuggingFace API token... 😔"
        elif "403 Client Error" in str(e):
            if "meta-llama" in model_map[model_name]:
                return """⚠️ You need access to use Llama models. Please:
1. Visit huggingface.co/meta-llama
2. Request access to Llama models
3. Accept the license terms
4. Wait for approval (processed hourly)"""
            else:
                return "⚠️ You don't have permission to use this model. Please request access first... 😔"
        else:
            return f"⚠️ An error occurred 😔: {str(e)}"

# Chat container for all messages
chat_container = st.container()

# Chat input with custom styling
if prompt := st.chat_input("What's on your mind? 💭"):
    if not hf_token:
        st.error("""
        ⚠️ Please set up your Hugging Face API token first:
        1. Create '.streamlit/secrets.toml'
        2. Add: HUGGINGFACE_API_TOKEN = "your_token_here"
        3. Get your token from: https://huggingface.co/settings/tokens
        """)
        st.stop()
    
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Prepare conversation history
    string_dialogue = ""
    for message in st.session_state.messages:
        if message["role"] == "user":
            string_dialogue += f"User: {message['content']}\n"
        else:
            string_dialogue += f"Assistant: {message['content']}\n"
    
    with st.spinner("✨ Thinking..."):
        response = generate_llama_response(prompt, string_dialogue)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat messages
with chat_container:
    st.markdown("""
    <style>
        .chat-bubble {
            margin: 10px 0;
            padding: 15px 20px;
            border-radius: 20px;
            max-width: 80%;
            position: relative;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .assistant-bubble {
            background: linear-gradient(135deg, #FFE4E1, #FFF0F5);
            border-radius: 20px 20px 20px 5px;
            margin-right: auto;
            color: #FF1493;
        }
        
        .user-bubble {
            background: linear-gradient(135deg, #FFE6E6, #FFF0F5);
            border-radius: 20px 20px 5px 20px;
            margin-left: auto;
            color: #FF1493;
        }
    </style>
    """, unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        bubble_class = "assistant-bubble" if message["role"] == "assistant" else "user-bubble"
        st.markdown(
            f'<div class="chat-bubble {bubble_class}">{message["content"]}</div>',
            unsafe_allow_html=True
        )
