from flask import Flask, request, jsonify
from transformers import pipeline
from transformers import T5ForConditionalGeneration, AutoTokenizer
import json
import re
import logging
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("news-summarisation-data")

app = Flask(__name__)

def remove_tags(text):
    #removing angular brackets from the string
    pattern = r'<[^>]*>'
    return re.sub(pattern, '', text)

@app.before_request
def before_request():
    global model, tokenizer
    app.logger.info('Before request')
    app.logger.info(request.headers)
    global model, tokenizer

    model = T5ForConditionalGeneration.from_pretrained('google-t5/t5-base',cache_dir='./model')
    tokenizer = AutoTokenizer.from_pretrained('google-t5/t5-base')

    app.logger.info("Model loaded and ready to use")


@app.route('/predict', methods=['POST'])
def predict():
    try:
        app.logger.info('Request recived')
        # Extract data from the request
        data = request.get_json(force=True)
        input_text = data["data"]
        response = table.get_item(Key={'article-input': input_text[:1000]})
        
        if 'Item' in response:
            print("Response : Item already present in DB")
            return jsonify(response['Item']['summ-result'])
        
        inputs = tokenizer("summarization: " + input_text, return_tensors="pt",max_length=512, truncation=True,stride=256,padding="max_length",return_overflowing_tokens=True, return_offsets_mapping=True)
        a,b = inputs['input_ids'].shape
        # Generate prediction
        part_summary =[]
        summary_ids = model.generate(inputs['input_ids'], num_beams=4, no_repeat_ngram_size=2, min_length=100, max_length=1024, early_stopping=True)
        for i in range(a):
            _ = tokenizer.decode(summary_ids[i], skip_special_tokens=True)
            part_summary.append(remove_tags(_))
        result = ''.join(part_summary)

        
        return jsonify(result)

    except Exception as e:
        app.logger.exception(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)

