from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

your_openai_api_key = ""  # OpenAI API key

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        messages = data.get('messages', [])

        openai_data = {
            "model": "gpt-3.5-turbo",
            "stream": True,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
            ],
        }

        openai_data["messages"].extend(messages)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {your_openai_api_key}',
        }

        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=openai_data, stream=True)

        for line in response.iter_lines():
            if line:
                try:
                    message = json.loads(line.decode('utf-8'))
                    choices = message.get('choices', [])
                    content = choices[0].get('message', {}).get('content', '')

                    if content:
                        return jsonify({'assistant_reply': content})
                except json.JSONDecodeError as e:
                    print(f'Error decoding JSON: {str(e)}')
                    return jsonify({'error': f'Error decoding JSON: {str(e)}'}), 500

        return jsonify({'error': 'No response from OpenAI'}), 500

    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/title', methods=['POST'])
def create_title():
    try:
        data = request.get_json()
        title = data.get('title', '')

        openai_data = {
            "model": "text-davinci-002",
            "prompt": f"Write a 3 words title for the following prompt: {title}",
            "max_tokens": 100,
            "temperature": 0.7,
            "n": 1,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {your_openai_api_key}',
        }

        response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=openai_data)

        try:
            data = response.json()
            title_completion = data.get('choices', [{}])[0].get('text', '')
            return jsonify({'title': title_completion})
        except json.JSONDecodeError as e:
            print(f'Error decoding JSON: {str(e)}')
            return jsonify({'error': f'Error decoding JSON: {str(e)}'}), 500

    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000, debug=True)
