import tkinter as tk
from tkinter import messagebox
import re
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows 전용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 키워드 사전
keywords = {
    "느림": ["느림", "느리다", "느려", "속도", "지연", "굼뜸", "대기", "기다림", "반응 없음"],
    "시끄러움": ["시끄럽", "음성", "소리", "크다", "크", "불쾌", "울림", "잡음", "귀아픔", "너무 큼"],
    "복잡함": ["어렵", "복잡", "헷갈림", "설명 부족", "불친절", "이해 안됨"],
    "고장": ["멈춤", "고장", "안됨", "안되", "먹통", "중단됨", "작동 안 함"],
    "빠름": ["빠르다", "빠름", "빨라", "속도 빠름", "신속", "즉시", "반응 빠름"],
    "편리함": ["편리", "간편", "쉽게", "직관적", "사용 쉬움"],
    "불편함": ["불편", "번거롭다", "불쾌", "이상함"],
    "만족": ["좋다", "좋아요", "만족", "최고", "완벽", "추천", "마음에 듬"]
}

def extract_rating(line):
    match = re.search(r"\[별점:\s*(\d)점\]", line)
    return int(match.group(1)) if match else None

def show_keyword_rating_chart(file="feedback.txt"):
    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        messagebox.showerror("오류", f"'{file}' 파일이 없습니다.")
        return

    keyword_ratings = {k: [] for k in keywords}
    for line in lines:
        rating = extract_rating(line)
        if not rating:
            continue
        for key, word_list in keywords.items():
            if any(w in line for w in word_list):
                keyword_ratings[key].append(rating)

    filtered = {k: v for k, v in keyword_ratings.items() if v}
    if not filtered:
        messagebox.showinfo("정보", "감지된 키워드가 없습니다.")
        return

    labels = list(filtered.keys())
    avg_ratings = [sum(v) / len(v) for v in filtered.values()]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, avg_ratings, color='orange')
    plt.ylim(0, 5)
    plt.ylabel("평균 별점")
    plt.title("키워드별 평균 별점")
    plt.tight_layout()
    for i, v in enumerate(avg_ratings):
        plt.text(i, v + 0.1, f"{v:.1f}", ha='center', fontsize=12)
    plt.show()

# ----- GUI -----

root = tk.Tk()
root.title("리뷰 수집")
root.geometry("1920x1080")

# 질문 문구
tk.Label(root, text="서비스는 만족하셨나요?", font=("Arial", 24)).pack(pady=(30, 10))

# 키워드 안내 + 통계 버튼
top_frame = tk.Frame(root)
tk.Label(top_frame, text="키워드로 짧게 작성", font=("Arial", 16)).pack(side="left", padx=10)
tk.Button(top_frame, text="리뷰 통계 보기", font=("Arial", 14), command=show_keyword_rating_chart).pack(side="left", padx=10)
top_frame.pack()

# 텍스트 입력창
txt = tk.Text(root, height=10, width=140, font=("Arial", 14))
txt.pack(pady=20)

# 별점 선택
star_frame = tk.Frame(root)
star_var = tk.IntVar(value=0)
stars = []
def update_stars(idx):
    for i in range(5):
        if i <= idx:
            stars[i].config(text='★', fg='gold')
        else:
            stars[i].config(text='☆', fg='gray')
    star_var.set(idx + 1)

for i in range(5):
    lbl = tk.Label(star_frame, text='☆', font=("Arial", 40), fg='gray', cursor="hand2")
    lbl.pack(side="left", padx=10)
    lbl.bind("<Button-1>", lambda e, idx=i: update_stars(idx))
    stars.append(lbl)
star_frame.pack(pady=20)

# 제출 버튼
def submit_feedback():
    rating = star_var.get()
    feedback = txt.get("1.0", tk.END).strip()
    if rating == 0 or not feedback:
        messagebox.showwarning("입력 오류", "별점과 피드백을 모두 입력해주세요.")
        return
    with open("feedback.txt", "a", encoding="utf-8") as f:
        f.write(f"[별점: {rating}점] {feedback}\n")
    messagebox.showinfo("완료", "피드백이 저장되었습니다.")
    root.destroy()

tk.Button(root, text="피드백 제출", command=submit_feedback, font=("Arial", 16),
          bg="green", fg="white", width=20, height=2).pack(pady=30)

root.mainloop()
