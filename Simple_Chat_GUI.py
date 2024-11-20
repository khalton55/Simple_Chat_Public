# Imports
import gradio as gr
import base64
import requests
import os
import json
##########################
import io

#Decodes audio response and saves to temp file
def decodeAudio(base64_string):
    try:
        audio_data = base64.b64decode(base64_string)

        outputAudioPath = 'reply.wav'
        with open(outputAudioPath, 'wb') as audio_file:
            audio_file.write(audio_data)

        return outputAudioPath

    except Exception as e:
        return str(e)

#Handles user input and send POST request to server
def query(query):
    warning = False
    if not isinstance(query, str):
        gr.Warning('Query is not a string!')
        warning = True

    query = query.strip()
    if not query:
        gr.Warning('Query cannot be empty!')
        warning = True

    if warning == True:
        return 'Check Warnings!', None
    
    current_dir = os.path.dirname(__file__)
    config_path = os.path.join(current_dir, './config/config.json')
    with open(config_path, 'r') as f:
        # ASSIGN BACKEND SERVER URL IN CONFIG.json
        data = json.load(f)
        url = data['backend_server_url']
    
    json_data = {'query': query}
    print(query)

    try:
        reply = requests.post(url, json=json_data, timeout=120)

        reply.raise_for_status()

        replyText = reply.json()['reply']

        replyAudioEncoded = reply.json()['file_data']

        replyAudio = decodeAudio(replyAudioEncoded)

        
        return replyText, replyAudio
    except requests.exceptions.HTTPError as error:
        error_json = reply.json()['Error']
        raise gr.Error(error_json)
        return error_json, None


#Annoying file access issue for directly referencing local file (Probably a better way but this works)
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


#App interface
with gr.Blocks() as app:
    image_path = './icon.webp'
    img_base64 = get_image_base64(image_path)
    gr.HTML(f'''
            <h1 style='text-align: center;'>Simple Chat </h1>
            <p style="text-align: center;">Ask the chatbot a question to start the conversation! Uses Llama2 LLM and Piper for TTS.</p>
            <img src="data:image/jpeg;base64,{img_base64}" width=\"500\" height=\"500\" style=\"display: block; margin-left: auto; margin-right: auto;\" >
            ''')
    
    queryTextBox = gr.TextArea(placeholder='Ask a Question!', label='Query')

    replyOutputAudio = gr.Audio(label="Reply TTS Output")

    replyOutputTextBox = gr.Text(label='Reply')
    
    submitButton = gr.Button('Submit')

    submitButton.click(
        fn=query,
        inputs=[queryTextBox],
        outputs=[replyOutputTextBox, replyOutputAudio]
    )

app.launch()