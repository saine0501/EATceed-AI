import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ValidationError
from apis.food_image import food_image_analyze, search_similar_food, rate_limit_user
from auth.decoded_token import get_current_member
from errors.custom_exceptions import InvalidJWT, AnalysisError

router = APIRouter(
    prefix="/v1/ai/food_image_analysis",
    tags=["음식 이미지 분석"]
)

# 음식 이미지 분석 API 테스트
@router.post("/test")
async def food_image_analysis_test():
    return {"success": "성공"}


# 리팩토링 과정에서 pydantic 위치 변경 진행할 예정
class ImageAnalysisRequest(BaseModel):
    # base64에 따른 문자열 타입 설정 
    food_image: str


# 음식 이미지 분석 API
@router.post("/")
async def analyze_food_image(image_base64: ImageAnalysisRequest, member_id: int = Depends(get_current_member)):
    
    # 인증 확인
    """
    비즈니스 예외처리 : 인증
    """
    if not member_id:
        raise InvalidJWT()
    
    """
    1. 요청 횟수 제한 구현(Redis)
    """

    # 남은 요청 횟수 
    remaining_requests = rate_limit_user(member_id)

    """
    2. food_image_analyze 함수를 통해 얻은 음식명(리스트 값)을 이용해 
    Elasticsearch 유사도 검색을 진행해 유사도가 높은 음식(들) 반환 진행
    """

    # OpenAI API를 이용한 이미지 분석: 음식명 결과 얻기
    
    # OpenAI API 호출로 이미지 분석 및 음식명 추출
    detected_food_data = food_image_analyze(image_base64.food_image)
    # 문자열로 반환된 데이터 JSON으로 변환
    detected_food_data = json.loads(detected_food_data)

    # 음식명 분석 결과가 없을 경우
    """
    비즈니스 예외처리 : 해당하는 음식을 분석할 수 없습니다. 
    """
    if not detected_food_data:
        raise AnalysisError("음식 분석 결과가 비어있습니다.")
        
    # 유사도 검색 결과 저장할 리스트 초기화
    similar_food_results = []

    # 유사도 검색 진행
    for food_data in detected_food_data:

        # 데이터 형식 확인 후 인덱싱 접근
        food_name = food_data["food_name"] if isinstance(food_data, dict) else None

        # 음식명 누락
        """
        만약에 식판사진을 예로 들어서, 5가지 음식 중 1개의 음식에서 food_name이 None이 존재 할 경우 
        해당 음식을 제외하고는 일단 실행이 되어야 한다.
        일단 "해당하는 음식을 분석할 수 없습니다" 예외처리로 진행
        """
        """
        비즈니스 예외처리 : 해당하는 음식을 분석할 수 없습니다.
        """
        if not food_name:
            raise AnalysisError("음식명 데이터가 누락되었습니다.")
        

        # 벡터 임베딩 기반 유사도 검색 진행
        similar_foods = search_similar_food(food_name)
        similar_food_list = [{"food_name": food["food_name"], "food_pk": food["food_pk"]} for food in similar_foods]

        # 반환값 구성
        similar_food_results.append({
            "detected_food": food_name,
            "similar_foods": similar_food_list
        })
    
    response = {
        "success": True,
        "response": {
            "remaining_requests": remaining_requests,
            "food_info": similar_food_results
        },
        "error": None
    }

    return response