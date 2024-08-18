from flask import Flask
from flask import make_response
import os
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

# image_path=os.path.join(os.getcwd(),"images")
image_path=os.path.join("/code/dingding","images")
@app.route('/image/<picname>')
def getImage(picname):
    picPath=os.path.join(image_path,picname)
    if  os.path.exists(picPath):
        image_data = open(picPath, "rb").read()
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    return picname
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)