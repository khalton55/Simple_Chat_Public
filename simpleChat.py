import os
import base64

#Flask
from flask import Flask, request, jsonify

#Token
from dotenv import load_dotenv

#Llama Auth
from huggingface_hub import login

#NanoLLM
from nano_llm import NanoLLM, ChatHistory
from nano_llm.utils import ArgParser
from nano_llm.plugins import AutoTTS, AudioRecorder

app = Flask(__name__)

#Setup models
def setup():
    try:
        load_dotenv()

        #Authenticate with Hugging Face
        api_token = os.getenv('HUGGING_FACE_API_TOKEN')
        print('Logging in to Hugging Face...')
        login(token = api_token)
        print('Logged in')

        #Load model
        print('Loading Llama2...')
        global model
        model = NanoLLM.from_pretrained(
            model='meta-llama/Llama-2-13b-chat-hf', 
            quantization='q4f16_ft', 
            api='mlc',
            api_token=api_token
        )
        print('Llama2 Loaded')

        #Create the chat history
        print('Creating Chat History...')
        global chat_history
        chat_history = ChatHistory(model, system_prompt="You are a helpful and friendly AI assistant. Don't use emojis when responding to the user. Only respond in english.")
        print('Chat History Created')

        #Add NanoLLM args and set custom (Piper settings)
        print('Setting up Args...')
        args = ArgParser(extras=['tts', 'audio_output', 'prompt', 'log', 'voice', 'voice-speaker']).parse_args()
        args.tts = 'piper'
        args.audio_output_file = './response.wav'
        args.verbose = True
        args.voice= 'en_US-hfc_male-medium'
        print(args)
        print('Args Set')

        #Setup TTS
        print('Setting Up and Starting TTS...')
        global tts
        tts = AutoTTS.from_pretrained(**vars(args))

        if args.audio_output_file is not None:
            tts.add(AudioRecorder(**vars(args)))

        #Starts TTS service
        tts.start()
        print('TTS Started')

        return 'Backend ready!'
    except Exception as error:
        print(f'ERROR: {error}')
        return 'Setup failed - See Error Above'

#Flask Route: /query POST
@app.route('/query', methods=['POST'])
def query():
    #Gets data from POST request
    request_data = request.get_json()

    #Extracts prompt from JSON
    prompt = request_data.get('query', None)
    
    print(f'Prompt: {prompt}')
    
    #Sanitize user input
    if not isinstance(prompt, str):
        return jsonify({'Error': 'Query must be a string!'}), 400
        
    prompt = prompt.strip()
    	
    if not prompt:
        return jsonify({'Error': 'No Query supplied!'}), 400
    
    #Add user prompt and generate chat tokens/embeddings
    chat_history.append('user', prompt)
    embedding, _ = chat_history.embed_chat()

    #Generate chat bot reply
    try:
        reply = model.generate(
            embedding, 
            streaming=False, 
            kv_cache=chat_history.kv_cache,
            stop_tokens=chat_history.template.stop,
            max_new_tokens=256,
        )
        reply = reply.replace('</s>', '')

        print(f'REPLY: {reply}')

        #Send reply text to TTS
        tts.process(reply)

        #Save reply to chat history
        chat_history.append('bot', reply)

        file_path = './response.wav'

        #Encode TTS response to send over JSON
        with open(file_path, 'rb') as file:
            encoded_file = base64.b64encode(file.read()).decode('utf-8')

        response = {
            'reply': reply,
            'file_data': encoded_file,
            'file_name': 'response.wav'
        }

        #Return reply and TTS file
        return jsonify(response), 200
    except Exception as error:
        return jsonify({'Error': f'{error}'}), 500
 

#Runs setup and starts app
if __name__ == '__main__':
    print(setup())
    app.run(host='0.0.0.0', debug=True, port=5001)
    
