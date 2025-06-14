**본 게시물의 저작권은 작성자에게 있으며, 허가 없는 복제 및 재배포는 금지됩니다.**
# ROS_Smart_Guided_Robot
- 4학년 1학기 캡스톤 디자인<br>
- [중간 평가 보고 PPT] (https://www.miricanvas.com/v/14m88l5) <br>
- [최종 보고 PPT] (https://www.miricanvas.com/v/14r0ktg)  <br>
- 사용 로봇 : 한백전자 SerBot AGV <br>
<img width="300" alt="Image" src="https://github.com/user-attachments/assets/d1ea4d69-8b30-4a51-a445-b27ba9ade347" style="float: left;"/><br>

## 사용 환경 및 프로그램
- Python 3.8.10
- PyQt5
- ROS2 Foxy
- OpenCV

## Front(4배속 GIF, 사용자 음성 인식 가능)
- Voice_Assistant_Sim_v3 단계 <br>
- 사용자 음성 인식[sklearn(models/voice_model.joblib), 텍스트 벡터화, 코사인유사도]
- 추후 마무리 단계에서 markov chain 쓰기.
<img src="https://github.com/user-attachments/assets/90536fb1-f2f2-4ea5-b686-ff5e5c59b678" width="500" style="float: left;" />


## Mapping
<img src="https://github.com/user-attachments/assets/7f7c75e4-9918-41b5-b912-bad5558dd65a" width="600"/><br>
<img src="https://github.com/user-attachments/assets/1b38b6ae-5c21-4c46-82c3-6aa7a9f16c93" width="600"/><br>
- A*경로탐색(다익스트라)

<img src="https://github.com/user-attachments/assets/8821ce18-af6c-4cfa-814d-ce773689614d" width="600"/><br>

현재까지의 비용 g(n) + 목표까지의 추정 비용 h(n)= f(n)이 가장 낮은 노드를 우선 탐색 <br>
```txt
heapq.heappush(heap, (f, node)): 우선순위 f를 기준으로 자동 정렬
heapq.heappop(heap): 가장 f값이 작은 노드를 O(log N) 시간에 꺼낼 수 있음
```
- 장애물 우클릭 토글(다시 A* 탐색을 자동으로 실행해서 경로를 업데이트) <br>

## Controller
<img src="https://github.com/user-attachments/assets/b8f4b778-98e2-4fb8-a781-d41dfa0eab36" width="500" style="float: left;" /> <br>




## Lidar 센서 기반 장애물 회피 
- 장애물 회피


## 주요 개발 과정 (Phase별)<br>
![프로젝트간트차트](https://github.com/user-attachments/assets/1f33c9f6-bfc3-4be0-b33e-17e6cdc0f097) <br>
