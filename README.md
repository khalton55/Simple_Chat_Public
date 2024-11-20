Example LLM and TTS Application using Llama2 and Piper TTS on NVIDIA Jetson
*Non-streaming*

Requirements:
NVIDIA Jetson with jetson-containers installed
Installed nano_llm:r36.3.0

To Run:
Client -
Edit config to include IP of machine running server
python3 Simple_Chat_GUI.py
(Most likely will have to install dependencies, will be fixed when able to make container)

Server - 
Add .env with hugging face token with acces to llama family of models
'HUGGING_FACE_API_TOKEN' is env variable name

Run this command while in repo directory
jetson-containers run -v .:/app --workdir /app --entrypoint /bin/bash dustynv/nano_llm:r36.3.0

pip install python-dotenv
(Jetson-containers doesnt come with this library so need this until containerization issue is solved)

python3 simpleChat.py


TODO:

Containerize once jetson-container build bug is fixed
Add support for flask on phone

Somehow fix how tts saves audio to same file and appends it instead of overwitting it

Streaming support?
Lower processing time
