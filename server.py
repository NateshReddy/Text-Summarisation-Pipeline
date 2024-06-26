from flask import Flask, request, jsonify
from transformers import pipeline
from transformers import T5ForConditionalGeneration, AutoTokenizer
# import json
import re
# import logging
import boto3

dynamodb = boto3.client('dynamodb', region_name = 'us-east-2')
table_name = "news-summarisation-data"
AWS_S3_CREDS = {
    "aws_access_key_id":"",
    "aws_secret_access_key":""
}
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-2', **AWS_S3_CREDS)
table = dynamodb.Table("news-summarisation-data")

# print("models are now starting to load")

model = T5ForConditionalGeneration.from_pretrained('google/t5-efficient-small-el16', cache_dir='./model')
tokenizer = AutoTokenizer.from_pretrained('google/t5-efficient-small-el16', cache_dir='./model')

# model.save_pretrained('model_small/')
# tokenizer.save_pretrained('model_small/')

# model = T5ForConditionalGeneration.from_pretrained('model_small/')
# tokenizer = AutoTokenizer.from_pretrained('model_small/')
print("models are loaded")

app = Flask(__name__)

def remove_tags(text):
    #removing angular brackets from the string
    pattern = r'<[^>]*>'
    return re.sub(pattern, '', text)

# @app.before_request
# def before_request():
#     global model, tokenizer
#     app.logger.info('Before request')
#     app.logger.info(request.headers)
#     global model, tokenizer

#     model = T5ForConditionalGeneration.from_pretrained('google-t5/t5-base',cache_dir='./model')
#     tokenizer = AutoTokenizer.from_pretrained('google-t5/t5-base', cache_dir='./model')

#     app.logger.info("Model loaded and ready to use")


@app.route('/predict', methods=['POST'])
def predict():
    try:
        app.logger.info('Request recived')
        # Extract data from the request
        data = request.get_json(force=True)
        input_text = data["data"]
        try:
            response = dynamodb.describe_table(TableName=table_name)
            if response['Table']['TableStatus'] == 'ACTIVE':
                print(f"Table '{table_name}' exists and is active.")

                # Get summary from the table
                try:
                    response = dynamodb.get_item(TableName=table_name, Key={'article-input': input_text[:1000]})
        
        if 'Item' in response:
            print("Response : Item already present in DB")
            return jsonify(response['Item']['summ-result'])
        
        print("Response : Generating Summary")
        inputs = tokenizer("summarization: " + input_text, return_tensors="pt",max_length=512, truncation=True,stride=256,padding="max_length",return_overflowing_tokens=True, return_offsets_mapping=True)
        a,b = inputs['input_ids'].shape
        # Generate prediction
        part_summary =[]
        summary_ids = model.generate(inputs['input_ids'], num_beams=4, no_repeat_ngram_size=2, min_length=100, max_length=1024, early_stopping=True)
        for i in range(a):
            _ = tokenizer.decode(summary_ids[i], skip_special_tokens=True)
            part_summary.append(remove_tags(_))
        result = ''.join(part_summary)

        
        # return jsonify(result)
        return jsonify('sometext')

    except Exception as e:
        app.logger.exception(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8080)

