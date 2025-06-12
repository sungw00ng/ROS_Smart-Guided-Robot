import re
import matplotlib.pyplot as plt
import tkinter as tk  # For messagebox
from tkinter import messagebox  # For messagebox
import numpy as np  # For radar chart calculations
from matplotlib.offsetbox import OffsetImage, AnnotationBbox  # For image insertion

# Korean font setting (Windows only)
# 한글 폰트 설정 (Windows 전용) - 한글이 깨지는 것을 방지
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Guide robot review 5 core items and related keywords dictionary
keywords = {
    "안전성": ["충돌 방지", "안전 거리", "경고", "위험", "안전", "충돌", "장애물 인식", "보행자 인식"],
    "정확성": ["목적지 도착률", "경로 이탈", "위치 인식", "지도 데이터", "신뢰성", "경로 재계산", "정확", "정밀"],
    "반응 속도": ["빠른 반응", "즉각", "지연 없음", "신속", "응답"],
    "편리성": ["사용자 인터페이스", "조작", "쉬움", "배터리 효율", "충전", "편리", "간편"],
    "적응력": ["날씨", "장애물", "교통 상황", "환경", "맞춤형", "적응", "다양한 환경"]
}

# Define evaluation item order (order to be displayed in UI)
evaluation_items_order_korean = ["안전성", "정확성", "반응 속도", "편리성", "적응력"]
evaluation_items_order_english = ["Safety", "Accuracy", "Responsiveness", "Convenience", "Adaptability"]

# Mapping from Korean to English labels for internal consistency
korean_to_english_labels = dict(zip(evaluation_items_order_korean, evaluation_items_order_english))


def extract_feedback_data(line):
    """
    Extracts ratings for each item and overall feedback content from feedback text.
    This function will still use Korean items for parsing the file as the file content uses Korean.
    """
    match_main = re.match(r"\[피드백\] (.*)", line)
    if not match_main:
        return None, None

    feedback_text = match_main.group(1).strip()
    ratings = {}
    for item_korean in evaluation_items_order_korean:  # Use Korean items to parse the file
        match_rating = re.search(rf"\[{item_korean}: (\d)점\]", feedback_text)
        if match_rating:
            ratings[item_korean] = int(match_rating.group(1))  # Store with Korean key for now
            # Remove the rating part from the feedback text to leave only pure feedback.
            feedback_text = re.sub(rf"\[{item_korean}: \d점\]", "", feedback_text).strip()

    return ratings, feedback_text.strip()


def show_keyword_rating_chart(file="feedback_robot.txt", image_path="image/remove_robot.png"):
    """
    Displays the average rating for each evaluation item in a radar chart and a horizontal bar chart,
    with an image inserted in the top-left corner.
    Labels on the charts will be in English.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Error", f"'{file}' file not found.")
        temp_root.destroy()
        return

    item_ratings = {item_korean: [] for item_korean in evaluation_items_order_korean}

    for line in lines:
        ratings_data, _ = extract_feedback_data(line)
        if ratings_data:
            for item_korean, rating in ratings_data.items():
                if item_korean in item_ratings:
                    item_ratings[item_korean].append(rating)

    filtered_items = {item_korean: ratings for item_korean, ratings in item_ratings.items() if ratings}

    if not filtered_items:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showinfo("Info", "No reviews collected or no evaluation items detected.")
        temp_root.destroy()
        return

    labels_english = [korean_to_english_labels[item_korean] for item_korean in evaluation_items_order_korean if
                      item_korean in filtered_items]
    avg_ratings = [sum(filtered_items[item_korean]) / len(filtered_items[item_korean]) for item_korean in
                   evaluation_items_order_korean if item_korean in filtered_items]

    # Create a figure with a GridSpec layout for two subplots
    fig = plt.figure(figsize=(18, 9))  # Adjust figure size for 1920x1080 screen
    gs = fig.add_gridspec(1, 2)  # 1 row, 2 columns

    # --- Radar Chart (Left Subplot) ---
    ax_radar = fig.add_subplot(gs[0, 0], projection='polar')
    ax_radar.set_title("Average Ratings (Radar Chart)", va='bottom', fontsize=18, fontweight='bold', color='#333333',
                       pad=40)

    num_vars = len(labels_english)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    avg_ratings_radar = avg_ratings + avg_ratings[:1]
    angles_radar = angles + angles[:1]

    ax_radar.set_theta_offset(np.pi / 2)  # Set the first axis pointing upwards
    ax_radar.set_theta_direction(-1)  # Align axes clockwise

    # Set axis labels (5-point scale)
    ax_radar.set_rgrids([1, 2, 3, 4], labels=[1, 2, 3, 4], fontsize=10, color='gray')  # Radial grid labels
    ax_radar.set_ylim(0, 5)  # Y-axis range (0 to 5 points)

    # Manually add '5' label slightly outside the 5.0 grid line for clarity
    ax_radar.text(ax_radar.get_xticks()[0], 5.1, "5", ha='center', va='bottom', fontsize=12, color='black',
                  fontweight='bold')

    # Add labels to each axis
    ax_radar.set_xticks(angles)  # Use all angles for xticks
    ax_radar.set_xticklabels(labels_english, fontsize=14, fontweight='bold', color='#555555',
                             y=0.1)  # Adjust y-position of axis labels

    # Plot data
    ax_radar.plot(angles_radar, avg_ratings_radar, color='#FFD700', linewidth=2, linestyle='solid',
                  label='Average Rating')  # Golden line for radar
    ax_radar.fill(angles_radar, avg_ratings_radar, color='#FFD700', alpha=0.25)  # Golden fill for radar

    # Display values at each data point
    for angle, rating in zip(angles, avg_ratings):
        ax_radar.text(angle, rating + 0.3, f"{rating:.1f}", ha='center', va='center', fontsize=12, fontweight='bold',
                      color='darkblue')

    # --- Horizontal Bar Chart (Right Subplot) ---
    ax_bar = fig.add_subplot(gs[0, 1])
    ax_bar.set_title("Average Ratings (Bar Chart)", fontsize=18, fontweight='bold', color='#333333')

    labels_bar_order = labels_english[::-1]
    avg_ratings_bar_order = avg_ratings[::-1]

    bars = ax_bar.barh(labels_bar_order, avg_ratings_bar_order, color='#4CAF50', height=0.6, edgecolor='black',
                       linewidth=1.5)  # Green bars
    ax_bar.set_xlim(0, 5.0)  # X-axis range from 0 to 5
    ax_bar.set_xlabel("Average Rating", fontsize=14, fontweight='bold', color='#555555')
    ax_bar.set_ylabel("Features", fontsize=14, fontweight='bold', color='#555555')
    ax_bar.tick_params(axis='x', labelsize=12)
    ax_bar.tick_params(axis='y', labelsize=14)
    ax_bar.invert_yaxis()  # Display top label at the top of the chart

    # Add numerical labels at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax_bar.text(width + 0.1, bar.get_y() + bar.get_height() / 2, f"{width:.1f}",
                    ha='left', va='center', fontsize=12, fontweight='bold', color='darkblue')

    # --- Add Image to the Figure ---
    try:
        # Load the image
        img = plt.imread(image_path)
        # Create an OffsetImage object
        imagebox = OffsetImage(img, zoom=0.2)  # Adjust zoom to change image size
        # Create an AnnotationBbox to place the image
        # xy is the data coordinates, xybox is the box coordinates, xycoords and boxcoords specify the coordinate system
        # pad=0, frameon=False removes padding and frame around the image
        # Adjusted Y-coordinate to move the image slightly down (from 0.95 to 0.90)
        ab = AnnotationBbox(imagebox, (0.05, 0.90), xycoords='figure fraction', boxcoords="figure fraction", pad=0,
                            frameon=False)
        fig.add_artist(ab)
    except FileNotFoundError:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Error", f"Image file not found: {image_path}")
        temp_root.destroy()
    except Exception as e:
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Error", f"Failed to load or place image: {e}")
        temp_root.destroy()

    plt.tight_layout(rect=[0.05, 0.05, 1, 0.95],
                     pad=3.0)  # Adjust layout to make space for the image, and ensure everything fits
    plt.show()


# Show the graph when this script is executed directly.
if __name__ == "__main__":
    show_keyword_rating_chart()
