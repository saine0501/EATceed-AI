from fastapi import HTTPException, status


"""
인증
1. 잘못된 인증 토큰
2. 만료된 인증 토큰
3. 존재하지 않은 유저
"""
# 잘못된 인증 토큰
class InvalidJWT(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "SECURITY_401_1", 
                "reason": "잘못된 인증 토큰 형식입니다.", 
                "http_status": status.HTTP_401_UNAUTHORIZED
            }
        )

# 만료된 인증 토큰 
class ExpiredJWT(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "SECURITY_401_2", 
                "reason": "인증 토큰이 만료되었습니다.", 
                "http_status": status.HTTP_401_UNAUTHORIZED
            }
        )   

# 존재하지 않은 유저 
class MemberNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "MEMBER_400_9",
                "reason": "존재하지 않는 회원입니다.",
                "http_status": status.HTTP_404_NOT_FOUND
            }
        )

"""
음식 이미지 분석
1. 기능 횟수 제한
2. 음식 이미지 분석 실패(OpenAI API)
"""

# 기능 횟수 제한
class RateLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "IMAGE_429_1",
                "reason": "하루 요청 제한을 초과했습니다.",
                "http_status": status.HTTP_429_TOO_MANY_REQUESTS
            }
        )


# 음식 이미지 분석 실패(OpenAI API)
class ImageAnalysisError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "IMAGE_400_1",
                "reason": "OpenAI API를 이용한 음식 이미지를 분석할 수 없습니다.",
                "http_status": status.HTTP_400_BAD_REQUEST
            }
        )

"""
식습관 분석
1. 유저의 분석 데이터가 없는 경우
2. 분석 진행 중인 경우
3. 분석 미완료 상태
"""

# 유저의 분석 데이터가 없는 경우
class UserDataError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DIET_404_1",
                "reason": "해당 유저에 대한 분석 데이터가 존재하지 않습니다.",
                "http_status": status.HTTP_404_NOT_FOUND
            }
        )

# 분석 진행 중인 경우
class AnalysisInProgress(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "DIET_409_1",
                "reason": "해당 유저에 대한 분석이 진행 중입니다.",
                "http_status": status.HTTP_409_CONFLICT
            }
        )

# 분석 미완료 상태
class AnalysisNotCompleted(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DIET_404_2",
                "reason": "분석이 아직 완료되지 않았습니다.",
                "http_status": status.HTTP_404_NOT_FOUND
            }
        )