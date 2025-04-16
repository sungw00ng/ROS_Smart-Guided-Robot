[사용 환경] <br>
Python 3.8.10<br>
PyQt5<br>
<br>
[PyQt5 특정 모듈]<br>
QtCore -> 이벤트 루프, 시그널과 슬롯 메커니즘, 타이머, 스레딩, 데이터 스트림, 설정, 공유 메모리, 파일 및 디렉토리 처리,  2D 기하 클래스 등<br>
QtGui ->  폰트, 브러쉬, 펜, 이미지, 색상, 커서, 마우스 및 키보드 이벤트 처리 등<br>
QtWidgets -> 버튼, 레이블, 텍스트 편집기, 리스트 뷰, 테이블 뷰, 다이얼로그, 메뉴, 툴바 등<br>
<br>
[적용 가능한 기능]<br>
주크박스 기능,<br>
사람 따라가기 기능 (객체 인식 3D Lidar 기반),<br>
음성 인식 결과를 보여주는 텍스트 영역과 특정 버튼들을 포함한,<br>
음성 비서 기능을 위한 컨트롤들을 제공.<br>
<br>

[loading]<br>
팀명인 AIMOB(AI_Mobility)를 Splash Screen 로딩창 이미지와 함께 가운데 로고처럼 시작할 예정.<br>
<br>
[실행 흐름]
1. loading 실행.<br>
2. Window 클래스의 인스턴스가 생성되어 UI가 표시<br>
3. QTimer를 사용하여 1초 후 window.load() 함수가 호출되어 필요한 리소스가 초기화되고 백그라운드 스레드 (ofth, gassth)가 시작됩니다.<br>
5. 사용자는 UI의 버튼을 통해 사람 따라가기, 주크박스, 음성 비서 기능을 선택하고 조작 가능.<br>
6. 사람 따라가기 기능이 활성화되면 카메라 영상이 처리되고 로봇이 제어됩니다.<br>
7. 주크박스 기능이 활성화되면 음악 재생 및 제어가 가능합니다.<br>
8. 음성 비서 기능이 활성화되면 Snowboy가 핫워드를 감지하고, 감지 시 Google Assistant를 통해 음성 명령을 처리하여 주크박스를 제어.<br>
9. 프로그램 종료 시 finally 블록에서 interrupted 변수를 True로 설정하여 스레드를 안전하게 종료.<br>
<br>
[용어 설명]<br>
ofth (Object Follow Thread)<br>
-주요 기능: 카메라로 사람을 인식하고 로봇을 움직여 따라감.<br>
-사용 가능 라이브러리: 영상 처리의 OpenCV, 수학 연산의 Math, 로봇 및 카메라 제어의 pop.Pilot 라이브러리를 사용.<br>
-GUI 상호작용: 인식된 사람의 모습이 담긴 영상을 GUI 화면에 보여줌.<br>
-스레드 클래스: 표준 파이썬의 threading.Thread를 사용하여 백그라운드에서 실행.<br>
<br>
gassth (Google Assistant Thread):<br>
주요 기능: 음성으로 특정 단어를 감지하고 Google Assistant를 통해 음성 명령을 처리하여 주크박스를 제어.<br>
사용 가능 라이브러리: 핫워드 감지의 Snowboy, Google Assistant 연동의 popAssist.GAssistant, 오디오 입출력의 pyaudio를 간접적으로 사용.<br>
GUI 상호작용: 인식된 음성 텍스트와 음성 인식 상태를 GUI에 표시하고, 주크박스 제어 신호를 GUI로 보냄.<br>
스레드 클래스: PyQt의 QThread를 상속받아 GUI 이벤트 루프와 더 잘 통합되어 실행.<br>
<br>
snowboy<br>
사용자 정의 핫워드 엔진으로, 핫워드(Hotword)는 특정 기능을 활성화시키기 위해 미리 지정해 놓은 단어나 구절을 의미.<br>
쉽게 설명하자면, 마치 "헤이 구글"이나 "오케이 구글"처럼 특정 "핫워드" (여기서는 Snowboy가 감지하는 특정 소리나 단어)를 말하면, 음성 비서 기능이 활성화되는 것.<br>
