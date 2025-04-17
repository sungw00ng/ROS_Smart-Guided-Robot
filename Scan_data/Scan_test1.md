**테스트 장소**<br>
3층 강의실<br>
<br>
**목적**<br>
Mapping <br>

**핸들**<br>
![Image](https://github.com/user-attachments/assets/6fbf289c-6f47-4a37-8695-05b8176540e8)<br>
키보드<br>
   W<br>
A  S  D<br>
   X<br>
W: 앞으로 가기<br>
A: 왼쪽으로 바퀴  회전<br>
S: 정지<br>
D: 오른쪽으로 바퀴 회전<br>
X: 뒤로 가기<br>
<br>
관측 값 3 종류(왼쪽부터)<br>
키보드 입력 터미널 / RViz맵데이터/ Steering 및 로봇 제어값<br>
<br>
**Scan1**<br>
SLAM(Simultaneous Localization and Mapping)<br>
![Image](https://github.com/user-attachments/assets/e6d3cc8a-b624-4eab-927d-5f6bee2eebc2)<br>
Check Option: 3d grid, LaserScan, Map, Path, TF <br>
3d lidar를 통한 경로 시각화를 확인할 수 있었음.<br>
<br>
**Scan2**<br>
Cost Map 혹은 Occupancy Grid  MAP<br>
![Image](https://github.com/user-attachments/assets/a817a4d6-a30a-4d1d-bae4-5af83f2155d5)<br>
파랑: 자유 공간<br>
하늘, 보라: 감지는 되었는데 불확실한 공간<br>
빨강, 분홍: 장애물 혹은 벽<br>
픽셀기반 맵으로 로봇 경로 계획 및 장애물 회피 등에 쓰이는 것을 확인함.<br>
