from flask import Flask,request,json

app = Flask(__name__)

@app.route('/')
def webhook():
    return 'Webhooks for OpenMetadata'

@app.route('/om-webhook',methods=['POST'])
def open_metadata_webhook():
    data = request.json
    print(data)
    return data

if __name__ == '__main__':
    app.run(debug=True)