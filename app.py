import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Thiết lập giao diện
st.set_page_config(page_title="📊 Game Review Explorer", page_icon="🎮")
st.title("🎮 Game Review Explorer")
st.markdown("""
Phân tích các bài đánh giá game từ người chơi thực tế, bao gồm thời lượng chơi, nhận xét, và rating.
""")

# Load dữ liệu
CSV_PATH = "sample_pred_results10k.csv"

@st.cache_data

def load_data():
    df = pd.read_csv(CSV_PATH)
    df['date_posted'] = pd.to_datetime(df['date_posted'])
    return df

df = load_data()

# Bộ lọc: chọn game
games = st.multiselect(
    "🎮 Chọn game để xem đánh giá:",
    options=df["title"].unique(),
    default=df["title"].unique()[:5]
)

# Lọc dữ liệu
df_filtered = df[df["title"].isin(games)]

# Hiển thị bảng dữ liệu
st.subheader("📋 Bảng dữ liệu đánh giá")
st.dataframe(df_filtered[[
    "date_posted", "title", "review", "playtime", "rating", "predicted_rating"
]], use_container_width=True)

# Biểu đồ 1: Trung bình rating & predicted rating theo game
st.subheader("📊 Biểu đồ rating thực tế và dự đoán theo game")
avg_ratings = df_filtered.groupby("title")[["rating", "predicted_rating"]].mean().reset_index()
avg_ratings = avg_ratings.melt(id_vars="title", var_name="Loại", value_name="Điểm trung bình")

bar_chart = (
    alt.Chart(avg_ratings)
    .mark_bar()
    .encode(
        x=alt.X("title:N", title="Game"),
        y=alt.Y("Điểm trung bình:Q"),
        color="Loại:N",
        tooltip=["title", "Loại", "Điểm trung bình"]
    )
    .properties(height=400)
)
st.altair_chart(bar_chart, use_container_width=True)

# Biểu đồ 2: Rating theo thời gian chơi
st.subheader("📈 Mối liên hệ giữa thời lượng chơi và rating")
scatter = (
    alt.Chart(df_filtered)
    .mark_circle(size=60)
    .encode(
        x=alt.X("playtime:Q", title="Thời gian chơi (giờ)"),
        y=alt.Y("rating:Q", title="Rating người dùng"),
        color="title:N",
        tooltip=["title", "review", "playtime", "rating", "predicted_rating"]
    )
    .interactive()
    .properties(height=400)
)
st.altair_chart(scatter, use_container_width=True)

# Tuỳ chọn xem toàn bộ đánh giá
with st.expander("📄 Xem toàn bộ nội dung đánh giá"):
    for _, row in df_filtered.iterrows():
        st.markdown(f"**🎮 {row['title']}** — {row['date_posted'].date()}")
        st.markdown(f"- ⏱ Thời gian chơi: **{row['playtime']} giờ**")
        st.markdown(f"- ⭐️ Rating thực tế: **{row['rating']}** — 🤖 Dự đoán: **{row['predicted_rating']}**")
        st.markdown(f"> {row['review']}")
        st.markdown("---")

# Thêm đánh giá mới
st.subheader("✍️ Nhập đánh giá game mới")
with st.form("review_form"):
    new_title = st.text_input("Tên game")
    new_review = st.text_area("Nội dung đánh giá")
    new_playtime = st.number_input("Thời gian chơi (giờ)", min_value=0)
    new_rating = st.slider("Rating thực tế", 1, 5, 3)
    submitted = st.form_submit_button("Lưu đánh giá")

    if submitted:
        new_entry = {
            "date_posted": datetime.now().strftime("%Y-%m-%d"),
            "funny": 0,
            "helpful": 0,
            "hour_played": new_playtime,
            "recommendation": "Recommended" if new_rating >= 3 else "Not Recommended",
            "review": new_review,
            "title": new_title,
            "rating": new_rating,
            "playtime": new_playtime,
            "review_length": len(new_review),
            "word_count": len(new_review.split()),
            "predicted_rating": new_rating
        }
        new_df = pd.DataFrame([new_entry])
        new_df.to_csv(CSV_PATH, mode='a', header=False, index=False)
        st.success("Đánh giá mới đã được lưu thành công! Hãy tải lại trang để xem cập nhật.")
