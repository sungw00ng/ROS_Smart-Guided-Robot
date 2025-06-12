import tkinter as tk
from tkinter import messagebox
import re
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 전용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 길 안내 로봇 리뷰 5가지 핵심 항목 및 관련 키워드 사전
# Guide robot review 5 core items and related keyword dictionary
keywords = {
    "안전성": ["충돌 방지", "안전 거리", "경고", "위험", "안전", "충돌", "장애물 인식", "보행자 인식"],
    "정확성": ["목적지 도착률", "경로 이탈", "위치 인식", "지도 데이터", "신뢰성", "경로 재계산", "정확", "정밀"],
    "반응 속도": ["빠른 반응", "즉각", "지연 없음", "신속", "응답"],
    "편리성": ["사용자 인터페이스", "조작", "쉬움", "배터리 효율", "충전", "편리", "간편"],
    "적응력": ["날씨", "장애물", "교통 상황", "환경", "맞춤형", "적응", "다양한 환경"]
}

# 평가 항목 순서 정의 (UI에 표시될 순서)
# Define evaluation item order (order to be displayed in UI)
evaluation_items_order = ["안전성", "정확성", "반응 속도", "편리성", "적응력"]


def extract_feedback_data(line):
    """
    피드백 텍스트에서 각 항목의 별점과 전체 피드백 내용을 추출합니다.
    Extracts ratings for each item and overall feedback content from feedback text.
    """
    match_main = re.match(r"\[피드백\] (.*)", line)
    if not match_main:
        return None, None

    feedback_text = match_main.group(1).strip()
    ratings = {}
    for item in evaluation_items_order:
        match_rating = re.search(rf"\[{item}: (\d)점\]", feedback_text)
        if match_rating:
            ratings[item] = int(match_rating.group(1))
            # 피드백 텍스트에서 별점 부분을 제거하여 순수한 피드백만 남깁니다.
            # Remove the rating part from the feedback text to leave only pure feedback.
            feedback_text = re.sub(rf"\[{item}: \d점\]", "", feedback_text).strip()

    return ratings, feedback_text.strip()


def show_keyword_rating_chart(file="feedback_robot.txt"):
    """
    각 평가 항목별 평균 별점을 차트로 보여줍니다.
    Displays the average rating for each evaluation item in a chart.
    """
    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        messagebox.showerror("오류", f"'{file}' 파일이 없습니다.")
        return

    item_ratings = {item: [] for item in evaluation_items_order}

    for line in lines:
        ratings_data, _ = extract_feedback_data(line)
        if ratings_data:
            for item, rating in ratings_data.items():
                if item in item_ratings:  # 정의된 항목만 처리
                    item_ratings[item].append(rating)

    # 데이터가 있는 항목만 필터링
    # Filter only items with data
    filtered_items = {item: ratings for item, ratings in item_ratings.items() if ratings}

    if not filtered_items:
        messagebox.showinfo("정보", "수집된 리뷰가 없거나 감지된 평가 항목이 없습니다.")
        return

    labels = list(filtered_items.keys())
    avg_ratings = [sum(v) / len(v) for v in filtered_items.values()]

    plt.figure(figsize=(12, 7))
    plt.bar(labels, avg_ratings, color='#4CAF50')  # 녹색 계열로 변경
    plt.ylim(0, 5)
    plt.ylabel("평균 별점", fontsize=14)
    plt.title("길 안내 로봇 평가 항목별 평균 별점", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    for i, v in enumerate(avg_ratings):
        plt.text(i, v + 0.1, f"{v:.1f}", ha='center', fontsize=12, fontweight='bold')
    plt.show()


# ----- GUI -----

root = tk.Tk()
root.title("길 안내 로봇 리뷰 수집")
root.geometry("1920x1080")  # Set window size to 1920x1080
root.resizable(False, False)  # Fix window size
root.configure(bg='#F0F0F0')  # Set background color

# Grid configuration to center main content in the root window
root.grid_rowconfigure(0, weight=1)  # Top padding
root.grid_rowconfigure(1, weight=1)  # Bottom padding
root.grid_columnconfigure(0, weight=1)  # Left padding
root.grid_columnconfigure(2, weight=1)  # Right padding

main_frame = tk.Frame(root, bg='#F0F0F0')
# Place main_frame in the center column (1) of root and set sticky='nsew' to expand
main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=50, pady=50)  # Spanning rows 0 and 1 of root

# Grid configuration for centering widgets within main_frame
main_frame.grid_rowconfigure(0, weight=1)  # Top padding within main_frame
main_frame.grid_rowconfigure(1, weight=0)  # Question label
main_frame.grid_rowconfigure(2, weight=0)  # Evaluation items container
main_frame.grid_rowconfigure(3, weight=0)  # Submit button
main_frame.grid_rowconfigure(4, weight=1)  # Bottom padding within main_frame

main_frame.grid_columnconfigure(0, weight=1)  # Left padding within main_frame
main_frame.grid_columnconfigure(1, weight=0)  # Content (no expansion)
main_frame.grid_columnconfigure(2, weight=1)  # Right padding within main_frame

# Question label
tk.Label(main_frame, text="길 안내 로봇에 대한 만족도를 평가해주세요!", font=("Arial", 48, "bold"), bg='#F0F0F0', fg='#333333').grid(
    row=1, column=1, pady=(30, 20), sticky='n')  # pady further reduced

# Evaluation items container
evaluation_items_container = tk.Frame(main_frame, bg='#F0F0F0')
evaluation_items_container.grid(row=2, column=1, pady=10)  # pady further reduced

# Grid configuration for aligning item names and star frames within the container
evaluation_items_container.grid_columnconfigure(0, weight=0)  # Item name column (no expansion)
evaluation_items_container.grid_columnconfigure(1, weight=1)  # Star column (expandable)

# Star selection for each evaluation item
item_star_vars = {item: tk.IntVar(value=0) for item in evaluation_items_order}
item_star_labels = {item: [] for item in evaluation_items_order}

for row_idx, item in enumerate(evaluation_items_order):
    # Item name label (first column)
    tk.Label(evaluation_items_container, text=item, font=("Arial", 32, "bold"), bg='#F0F0F0', fg='#555555').grid(
        row=row_idx, column=0, padx=(0, 20), pady=5, sticky='w')  # padx, pady further reduced

    # Frame to hold star labels (second column)
    star_inner_frame = tk.Frame(evaluation_items_container, bg='#F0F0F0')
    star_inner_frame.grid(row=row_idx, column=1, pady=5, sticky='w')  # pady further reduced


    def update_item_stars(current_item, idx):
        for i in range(5):
            if i <= idx:
                item_star_labels[current_item][i].config(text='★', fg='gold')
            else:
                item_star_labels[current_item][i].config(text='☆', fg='gray')
        item_star_vars[current_item].set(idx + 1)


    for i in range(5):
        lbl = tk.Label(star_inner_frame, text='☆', font=("Arial", 96), fg='gray', cursor="hand2",
                       bg='#F0F0F0')  # Star font size unchanged (96)
        lbl.pack(side="left", padx=5)  # padx further reduced
        lbl.bind("<Button-1>", lambda e, item_name=item, idx=i: update_item_stars(item_name, idx))
        item_star_labels[item].append(lbl)


# Submit button
def submit_feedback():
    all_ratings_entered = True
    feedback_parts = []
    for item in evaluation_items_order:
        rating = item_star_vars[item].get()
        if rating == 0:
            all_ratings_entered = False
            break
        feedback_parts.append(f"[{item}: {rating}점]")

    if not all_ratings_entered:
        messagebox.showwarning("입력 오류", "모든 평가 항목에 별점을 입력해주세요.")
        return

    full_feedback_line = f"[피드백] {' '.join(feedback_parts)}\n"

    try:
        with open("feedback_robot.txt", "a", encoding="utf-8") as f:
            f.write(full_feedback_line)
        messagebox.showinfo("완료", "피드백이 성공적으로 저장되었습니다.")
        root.destroy()  # Close window
    except Exception as e:
        messagebox.showerror("오류", f"피드백 저장 중 오류 발생: {e}")


tk.Button(main_frame, text="피드백 제출", command=submit_feedback, font=("Arial", 36, "bold"),  # Font size unchanged
          bg="#28A745", fg="white", activebackground="#218838", relief="raised", bd=4, width=18, height=2).grid(row=3,
                                                                                                                column=1,
                                                                                                                pady=30,
                                                                                                                sticky='n')  # pady further reduced

root.mainloop()
