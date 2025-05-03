import boto3
import json

def encode_korean_to_utf8(obj):
    if isinstance(obj, dict):
        return {k: encode_korean_to_utf8(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [encode_korean_to_utf8(elem) for elem in obj]
    elif isinstance(obj, str):
        return obj.encode('utf-8').decode('utf-8')
    else:
        return obj

def bedrock_chatbot(input_text):
    # Bedrock runtime 클라이언트 생성
    client = boto3.client('bedrock-runtime')

    # Bedrock 모델 호출
    response = client.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',  # 실제 모델 ID로 교체
        body=json.dumps({
            'messages': [
                {'role': 'user', 'content': input_text}
            ],
            'max_tokens': 512,
            'anthropic_version': 'bedrock-2023-05-31'  # 올바른 버전으로 교체
        }),
        contentType='application/json'
    )
    
    response_body = response['body'].read().decode('utf-8')
    response_json = json.loads(response_body)
    # 한글을 UTF-8로 인코딩
    response_json = encode_korean_to_utf8(response_json)
    return response_json

def lambda_handler(event, context):
    try:
        # 입력 데이터 추출
        ingredients = event.get('ingredients', [])
        servings = event.get('servings', 1)
        
        # 자연어 질의문 생성
        ingredients_list = ", ".join(ingredients)
        natural_language_query = (
            f"Calculate and provide only the numerical values for the five main nutrients (calories, carbohydrates, fats, proteins, sodium) "
            f"in the combined food from the given ingredients and amounts. Use the following format for the answer: "
            f"{{'칼로리': 'kcal', '탄수화물': 'g', '지방': 'g', '단백질': 'g', '나트륨': 'mg'}}. "
            f"Ensure calculations are based on a per-serving basis, and prioritize fresh and dried ingredients from the data source. "
            f"Ingredients: {ingredients_list}, servings: {servings}. "
            f"Provide the answer in the specified format without any additional conversational elements."
        )

        # Bedrock 모델 호출
        response = bedrock_chatbot(natural_language_query)
        
        return {
            'statusCode': 200,
            'body': json.dumps(response, ensure_ascii=False)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}, ensure_ascii=False)
        }