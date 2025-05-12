# ROS_Smart_Guided_Robot
- 4학년 1학기 캡스톤 디자인<br>
- 사용 로봇 : 한백전자 SerBot AGV <br>

<img width="300" alt="Image" src="https://github.com/user-attachments/assets/d1ea4d69-8b30-4a51-a445-b27ba9ade347" style="float: left;"/><br>

## 사용 환경 및 프로그램
- Python 3.8.10
- PyQt5
- ROS2 Foxy
- OpenCV

## Front(4배속 GIF, 사용자 음성 인식 가능)
- VoiceAssitant_v3.2 단계 <br>
(worker[박성웅] for v4: Markov Chain을 활용한 다양한 상황 예제 AI 학습)
<img src="https://github.com/user-attachments/assets/803a1efd-28b6-4fbf-b711-a2c0620a0576" width="500" style="float: left;" />


## Mapping
- ROS2로 Mapping <br> <br>

- 3층 복도 <br>
<img src="https://github.com/user-attachments/assets/60f9d9b1-f77e-43a1-b71c-45f9e7b0530c" width="500" style="float: left;" /> <br>

- 313호<br>
<img src="https://github.com/user-attachments/assets/8e3fc329-4c83-4df3-ac36-90aa32fad695" width="500" style="float: left;" /> <br>

## Controller
<img src="https://github.com/user-attachments/assets/b8f4b778-98e2-4fb8-a781-d41dfa0eab36" width="500" style="float: left;" /> <br>


## Navigation <br>
- worker[채형주, 원정식] for Nav2, Example <br>
<img src="https://github.com/user-attachments/assets/61068492-390b-432e-82ce-d279049c9425" width="500" style="float: left;" /> <br>


## OpenCV
- worker[이정재, 안상겸, 한명규] for door 객체 인식 훈련 , Example <br>
- 최단 경로 연구 중 <br>
<img width="500" alt="Image" src="https://github.com/user-attachments/assets/19165ad8-5618-4e21-82d6-5a00402ad3e0" style="float: left;" /><br>

## 주요 개발 과정 (Phase별)<br>
![프로젝트간트차트](https://github.com/user-attachments/assets/1f33c9f6-bfc3-4be0-b33e-17e6cdc0f097) <br>

**역할 분담**<br>
채형주: SLAM (지도 작성) 알고리즘 설정 및 지도 생성.<br>
박성웅: 음성 합성(TTS) 및 로봇 디스플레이<br>
원정식: 네비게이션 자율 주행 <br>
이정재: OpenCV를 활용한 장애물 감지 회피<br>
안상겸: 센서 인터페이스 (LiDAR, 카메라) 및 AI 인식 (사람 인식)<br>
한명규: OpenCV를 활용한 객체 추적 <br>
