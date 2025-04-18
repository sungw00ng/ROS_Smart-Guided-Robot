<h2>ROS_Smart_Guided_Robot</h2> <br>
4학년 1학기 캡스톤 디자인<br>
사용 로봇 : 한백전자 SerBot AGV<br>
<img width="497" alt="Image" src="https://github.com/user-attachments/assets/d1ea4d69-8b30-4a51-a445-b27ba9ade347" /><br>
제품 특징<br>
클러스터 컴퓨팅 기반 인공지능(인지/판단)유닛과 고성능 MCU 기반 운영제어유닛<br>
딥러닝 기반 실내용 서비스로봇 개발 플랫폼<br>
<br>

**목표**<br>
ROS 2 기반의 자율 이동 안내 로봇(SerBot AGV) 개발 및 운용. <br>
사용자가 지정한 목적지까지 안전하게 자율 주행하고,<br>
기본적인 사람 인식 기능을 통해 상호작용 기반 마련.<br>
<br>
**주요 개발 내용**<br>
ROS 2 기본 환경 구축: Foxy 설치, 작업 공간 생성 및 빌드, 로봇 설정 패키지 생성.<br>
**로봇 하드웨어 인터페이스**<br>
모터 제어: /cmd_vel 토픽 구독하여 모터 구동.<br>
LiDAR 연동: /scan 토픽으로 데이터 발행.<br>
카메라 연동: /image_raw 토픽으로 영상 발행.<br>
로봇 모델링 (URDF): 링크, 조인트, 센서 위치 정의 및 TF 트리 발행.<br>
SLAM (지도 작성): LiDAR와 TF를 이용하여 2D 점유 격자 지도 생성 및 저장.<br>
Localization (위치 추정): 저장된 지도, LiDAR, TF를 이용하여 실시간 로봇 위치 및 방향 추정.<br>
<br>
**Navigation (자율 주행)**<br>
Navigation2 스택 설정 (Costmap, Planner, Controller, Behavior Tree).<br>
목표 지점 전달 인터페이스 구현 (RViz2).<br>
인공지능 기능 (사람 인식): 카메라 영상 기반 딥러닝 모델을 통해 사람 위치 감지 및 결과 토픽 발행.<br>
안내 로봇 통합 로직 및 상호작용:<br>
중앙 제어 노드 ("Brain"): 목적지 입력, 로봇 상태 모니터링, Navigation2 목표 전달, 안내 시나리오 관리.<br>
목적지 입력 인터페이스 (ROS 2 토픽).<br>
사용자 피드백: 음성 합성(TTS) 및 로봇 디스플레이 출력.<br>
<br>
**주요 개발 과정 (Phase별)**<br>
![프로젝트간트차트](https://github.com/user-attachments/assets/1f33c9f6-bfc3-4be0-b33e-17e6cdc0f097) <br>
Phase 1 (1-2주차): ROS 2 기본 환경 구축 및 로봇 기본 구동 (URDF, 모터, LiDAR, 카메라 연동).<br>
Phase 2 (3주차): SLAM을 통한 지도 작성 및 작성된 지도를 이용한 Localization 설정 및 테스트.<br>
Phase 3 (4-5주차): Navigation2 스택 설정 및 기본적인 자율 주행 테스트 및 파라미터 튜닝.<br>
Phase 4 (6-8주차): 카메라 기반 사람 인식 AI 노드 개발 및 통합, 목적지 입력/피드백 인터페이스 개발, 중앙 제어 노드 개발.<br>
Phase 5 (9주차): 전체 시스템 통합, 실제 환경에서의 안내 시나리오 테스트, 성능 평가 및 문서화.<br>
<br>
**역할 분담**<br>
팀원 1: 센서 인터페이스 (LiDAR, 카메라) 및 AI 인식 (사람 인식).<br>
팀원 2: 액추에이터 (모터 제어) 및 중앙 제어 ("Brain").<br>
팀원 3: 로봇 모델링 (URDF) 및 TF(Transform) 관리.<br>
팀원 4: SLAM (지도 작성) 알고리즘 설정 및 지도 생성.<br>
팀원 5: Localization (위치 추정) 설정 및 성능 최적화, TF 트리 검증.<br>
팀원 6: Navigation2 스택 (Costmap, Planner, Controller, Behavior Tree) 설정 및 튜닝.<br>
