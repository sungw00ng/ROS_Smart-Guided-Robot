🚀 목표: 조이스틱 없이 Waypoint만으로 완전 자율 주행
✅ 전제 조건
직접 만든 속도 제어 코드 있음 (예: /cmd_vel 또는 /diff_cont/cmd_vel_unstamped 받아서 바퀴 돌림)

ros2_control, twist_mux 안 씀

SLAM으로 만든 맵 존재

AMCL을 통해 위치 추정

Nav2 사용

📂 기본 구성 요약

구성 요소	설명
AMCL	기존 맵 기반으로 로봇 위치 추정
Nav2	목표점까지 경로 계산, 속도 명령 생성
LiDAR	실시간 장애물 감지
RViz2	맵 시각화 + Waypoint 지정
직접 만든 코드	/cmd_vel 메시지를 받아 바퀴 제어
🔧 파일 구성
arduino
복사
편집
your_ws/
├── src/
│   └── your_package/
│       ├── launch/
│       │   ├── localization.launch.py
│       │   └── navigation.launch.py
│       └── config/
│           ├── amcl_params.yaml
│           └── nav2_params.yaml
├── install/
├── build/
└── map/
    ├── my_map.yaml
    └── my_map.pgm
🧭 1. localization.launch.py
python
복사
편집
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='map_server',
            executable='map_server',
            name='map_server',
            parameters=['map/my_map.yaml'],
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=['config/amcl_params.yaml'],
        ),
    ])
🧭 2. navigation.launch.py
python
복사
편집
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            parameters=['config/nav2_params.yaml'],
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=['config/nav2_params.yaml'],
            remappings=[('/cmd_vel', '/your_custom_cmd_vel')],
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=['config/nav2_params.yaml'],
        ),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=['map/my_map.yaml'],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            parameters=[{'autostart': True}, {'node_names': [
                'bt_navigator', 'controller_server', 'planner_server', 'map_server'
            ]}]
        )
    ])
⚙️ 3. 속도 제어 코드 예시 (파이썬)
python
복사
편집
from geometry_msgs.msg import Twist

def cmd_vel_callback(msg):
    linear = msg.linear.x
    angular = msg.angular.z
    # 바퀴 속도 계산 및 모터 드라이버에 전달
    left = linear - angular * 0.5
    right = linear + angular * 0.5
    motor_driver.set_speed(left, right)

rclpy.create_subscription(Twist, '/your_custom_cmd_vel', cmd_vel_callback, 10)
🎯 4. 실행 순서
라이다 드라이버 실행 (예: rplidar, sllidar, velodyne)

속도 제어 노드 실행 (위의 파이썬 코드)

localization 실행

bash
복사
편집
ros2 launch your_package localization.launch.py
navigation 실행

bash
복사
편집
ros2 launch your_package navigation.launch.py
RViz 실행 후:

맵 로딩 확인

Navigation2 패널 추가

Nav2 Goal Tool 추가

"Waypoints" 모드로 클릭 + Start Navigation 누르기!

🎉 결과
/your_custom_cmd_vel로 Nav2가 속도 명령 보냄

당신이 만든 노드가 이걸 받아 바퀴 돌림

Waypoint만 찍으면 자율주행 끝!
