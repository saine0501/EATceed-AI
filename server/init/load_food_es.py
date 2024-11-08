import os
import time
import pandas as pd
from core.config import settings
from elasticsearch import Elasticsearch, helpers


# Elasticsearch 클라이언트 설정
es = Elasticsearch(
    settings.ELASTICSEARCH_HOST, 
    basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD))


# 인덱스 이름 설정
index_name = "food_names"


# 인덱스 매핑 생성
if not es.indices.exists(index=index_name):
    # Standard 분석기 및 임베딩 벡터 필드를 포함한 인덱스 설정
    es.indices.create(
        index=index_name,
        body={
            "settings": {
                "index": {
                    "analysis": {
                        "analyzer": {
                            "standard_analyzer": {
                                "type": "standard"
                            }
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "food_pk": {
                        "type": "integer"
                    },
                    "food_name": {
                        "type": "text",
                        "analyzer": "standard_analyzer",
                        "search_analyzer": "standard"
                    },
                    "embedding": {
                        "type": "dense_vector",
                        # 임베딩 차원: 512도 가능
                        "dims": 1536  
                    }
                }
            }
        }
    )



# 데이터셋 불러오기
df = pd.read_csv(os.path.join(settings.DOCKER_DATA_PATH, "food.csv"))


# '_'(underbar)를 공백으로 대체 : 해당 로직 적용시 pk 값 찾지 못해 사용하지 않음
# df['FOOD_NAME'] = df['FOOD_NAME'].str.replace('_', ' ')


# Elasticsearch에 적재할 데이터 준비
actions = []
for _, row in df.iterrows():
    # 문자열 형태의 리스트를 리스트로 변환
    embedding = eval(row['EMBEDDING'])  
    actions.append({
        "_index": index_name,
        "_source": {
            "food_pk": row["FOOD_PK"],
            "food_name": row['FOOD_NAME'],
            "embedding": embedding
        }
    })

# 시간 측정 시작
start_time = time.time()

# Bulk API로 데이터 적재
helpers.bulk(es, actions)

# 시간 측정 종료
end_time = time.time()
print(f"Elasticsearch 인덱스 '{index_name}'에 음식명과 임베딩이 함께 적재되었습니다.")
print(f"총 소요 시간: {end_time - start_time:.2f}초")