from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from app.dissection import dissection, results_img
import tensorflow as tf
from glob import glob
import re
import numpy as np


tf.enable_eager_execution()

UPLOAD_FOLDER = 'app/static/model'
IMG_FOLDER = 'app/static/img'
ALLOWED_EXTENSIONS = {'pb'}
ALLOWED_EXTENSIONS_IMG = {'jpg', 'png'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMG_FOLDER'] = IMG_FOLDER

CORS(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file_img(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG



@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Hello'


@app.route('/model', methods=['GET', 'POST'])
def model():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tf_model.pb')
    if os.path.isfile(file_path):
        
        return jsonify({'data': True})
    return jsonify({'data': False})

@app.route('/modelcek', methods=['GET', 'POST'])
def modelcek():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'tf_model.pb')
    if os.path.isfile(file_path):
        l, ld = dissection(file_path)
        return jsonify({'layers': l, 'layers_dict': ld })
    return jsonify({'data': False})



@app.route('/upload', methods=['POST'])
def upload():
    print(request.files)
    if 'file' not in request.files:
        return 'Ga ada file yang diupload'
    file = request.files['file']
    if file.filename == '':
        return 'Ga ada file yang diupload'
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'Uploaded'


@app.route('/uploadgambar', methods=['POST'])
def uploadgambar():
    if 'file' not in request.files:
        return 'Ga ada file yang diupload'
    file = request.files['file']
    if file.filename == '':
        return 'Ga ada file yang diupload'
    if file and allowed_file_img(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['IMG_FOLDER'], filename))
            return filename

@app.route('/results', methods=['POST'])
def results():
    filename = os.path.join(app.config['IMG_FOLDER'], request.form['filename'])
    ops = request.form.getlist('ops[]')
    folders = []
    for op in ops:
        o = re.split('/', op)
        if not os.path.isdir(os.path.join(app.config['IMG_FOLDER'], 'ops/' + o[0])):
            os.makedirs(os.path.join(app.config['IMG_FOLDER'], 'ops/' + o[0]))
        folders.append(os.path.join(app.config['IMG_FOLDER'], 'ops/' + o[0]))   
    results_img(filename, ops, folders)
    op_folder = [re.split('/', o)[0] for o in ops ]
    urls = get_images(op_folder)
    return jsonify(urls)

@app.route('/gallery', methods=['GET'])
def galley():
    folder = os.path.join(app.config['IMG_FOLDER'], 'ops')
    
    labels = next(os.walk(folder))[1]
    # files = glob(folder + '/**/*.png')
    imgs = {}
    for l in labels:
        files = glob(folder + '/' + l + '/*.png')
        urls = ['http://127.0.0.1:8000/static/img/ops/' + l + '/' + os.path.basename(file) for file in files]
        imgs[l] = urls
    return imgs


def get_images(ops):
    imgs = {}
    for op in ops:
        folders = os.path.join(app.config['IMG_FOLDER'], op)
        files = glob(folders + '/*.png')
        urls = ['http://127.0.0.1:8000/static/img/' + op + '/' + os.path.basename(file) for file in files]
        imgs[op] = urls
    return imgs
