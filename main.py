import flask
import io
import string
import time
import os
import numpy as np
import torch
import torchvision
import cv2
from PIL import Image
import albumentations as A
from flask import Flask, jsonify, request

model = torch.load('modelCovid19.pth', map_location ='cpu')
model.eval()

transform = A.Compose(
        [A.Resize(300,300),
         A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))])


def prepare_img(img):
    im = Image.open(io.BytesIO(img))
    im = np.array(im)
    im = transform(image=im)['image']
    im = torch.tensor(im/255).to('cpu').float()
    im = im.unsqueeze(0).permute(0, 3, 1, 2)
    return im


def preds(x, model):
    with torch.no_grad():
        model.eval()
        prediction = model(x)
    prediction = prediction.to('cpu').detach().numpy()
    prediction = "Normal" if prediction >= 0.5 else "Covid-19"
    return prediction


app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def infer_image():
    if 'file' not in request.files:
        return "Please try again. The Image doesn't exist"

    file = request.files.get('file')

    if not file:
        return

    img_bytes = file.read()
    img = prepare_img(img_bytes)

    return jsonify(prediction=preds(img, model))


@app.route('/', methods=['GET'])
def index():
    return 'Machine Learning Inference'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')








