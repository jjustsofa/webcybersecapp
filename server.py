import cv2
import pytesseract
import re
import transformers
from flask import Flask, request, send_file
from numpy import uint8, frombuffer, array
from flask_cors import CORS
from base64 import b64encode
from json import loads
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO

app = Flask(__name__)
CORS(app)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



def names(text):
    messages = [
        [
            {
                "role": "system",
                "content": [{"type": "text", "text": '''проанализируй текст и выведи только имена'''}, ]
            },
            {
                "role": "user",
             "content": [{"type": "text", "text": "Вот текст:\n" + text}]
            }
        ],
    ]

    prompt = tokenizer.apply_chat_template(messages, tokenize=True, return_tensors='pt', add_generation_prompt=True)
    outputs = model.generate(prompt, max_new_tokens=500)
    data = tokenizer.decode(outputs[0])

    return data[data.index('model') + 5:data.rindex('<')].replace('\n', ' ')


def gen(bytecode, settings, cv_type=False):
    if cv_type:
        img = bytecode
    else:
        img = cv2.imdecode(frombuffer(bytecode, uint8), cv2.IMREAD_ANYCOLOR)
    data = pytesseract.image_to_data(img, lang='rus+eng', output_type=pytesseract.Output.DICT)
    parsed_data = {}

    snils_pattern = r'^\d{3}[- ]?\d{3}[- ]?\d{3}[- ]?\d{2}$'


    inn_pattern = r'^\d{10}$|^\d{12}$'


    passport_seria_pattern = r'\d{4}'
    passport_number_pattern = r'\d{6}'


    phone_pattern = r'^(\+7|8)[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}$'

    oms_policy_pattern = r'^(\d{16}|\d{6}[ -]\d{8}|(\d{4}[ -]?){3}\d{4})$'

    for i in range(len(data['text'])):
        sim = data['text'][i]
        if not sim:
            continue
        if sim in parsed_data.keys():
            parsed_data[sim].append(((data['top'][i], data['left'][i]), (data['width'][i], data['height'][i])))
        else:
            parsed_data[sim] = [((data['top'][i], data['left'][i]), (data['width'][i], data['height'][i]))]

    fios = ''
    if 'fio' in settings:
        fios = names(' '.join([i for i in data['text'] if len(i) >= 2 and not set(i) & set('1234567890!@#$%^&*()?') ])).split()

    for i in parsed_data.keys():
        if (('phone' in settings and re.search(phone_pattern, i)) or
                ('email' in settings and i.count('@')) or
                (i in fios) or
                ('inn' in settings and re.search(inn_pattern, i)) or
                ('snils' in settings and re.search(snils_pattern, i)) or
                ('oms' in settings and re.search(oms_policy_pattern, i)) or
                ('passport' in settings and re.search(passport_seria_pattern, i)) or
                ('passport' in settings and re.search(passport_number_pattern, i))
        ):
            for (y, x), (w, h) in parsed_data[i]:
                poi = img[y:y+h, x:x+w]
                blur = cv2.GaussianBlur(poi, (51, 51), 0)
                img[y:y + h, x:x + w] = blur

    if cv_type:
        return img

    return cv2.imencode('.png', img)[1]


def pdf_gen(imgs, settings):
    data = []
    for i in imgs:
        data.append(Image.fromarray(gen(cv2.cvtColor(array(i), cv2.COLOR_RGB2BGR), settings, cv_type=True)))
    pdf = BytesIO()
    data[0].save(pdf, format='pdf', resolution=100.0, save_all=True, append_images=data[1:])
    return pdf.getvalue()


@app.route('/', methods=['POST'])
def main():
    settings = loads(request.form['documentJson'])
    settings = [i for i in settings.keys() if settings[i]]

    if 'pdf' in settings:
        data = pdf_gen([cv2.cvtColor(array(i), cv2.COLOR_RGB2BGR) for i in convert_from_bytes(request.files['file'].read())], settings)
    else:
        data = gen(request.files['file'].read(), settings)
    return b64encode(data), 200


@app.route('/sogl')
def lol():
    return send_file('Пользовательское соглашение.pdf')


if __name__ == "__main__":
    print('start init model')
    from transformers import Gemma3ForCausalLM, AutoTokenizer

    transformers.set_seed(2025)

    tokenizer = AutoTokenizer.from_pretrained('./gemma/')
    model = Gemma3ForCausalLM.from_pretrained('./gemma/').eval()

    print('model has been initialized')

    app.run(port=8080)

