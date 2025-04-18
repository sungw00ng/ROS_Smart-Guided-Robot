import speech_recognition as sr

# 인식기 초기화
recognizer = sr.Recognizer()

# 마이크를 소스로 설정
with sr.Microphone() as source:
    print("🎤 말해주세요...")
    recognizer.adjust_for_ambient_noise(source)  # 주변 소음 보정
    audio = recognizer.listen(source)

    try:
        # 구글 웹 API로 음성 인식
        text = recognizer.recognize_google(audio, language="ko-KR")
        print("인식된 텍스트:", text)
    except sr.UnknownValueError:
        print("음성을 인식하지 못했습니다.")
    except sr.RequestError as e:
        print(f"구글 API 요청 실패: {e}")
