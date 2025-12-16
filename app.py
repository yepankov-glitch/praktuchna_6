import streamlit as st
import sqlite3
from datetime import date
import random
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Список фільмів Довженко Топ-100
# (можна розширювати або замінити на повний список)
# ---------------------------
DOVZHENKO_TOP_100 = [
    "Земля (1930)",
    "Тіні забутих предків (1964)",
    "Людина з кіноапаратом (1929)",
    "Ентузіязм (1931)",
    "Криниця для спраглих (1965)",
    "Вавилон ХХ (1979)",
    "Білий птах з чорною ознакою (1971)",
    "Пропала грамота (1972)",
    "Камінний хрест (1968)",
    "Поводир (2014)",
    "Плем'я (2014)",
    "Мої думки тихі (2019)",
    "Захар Беркут (1971)",
    "Атлантида (2019)",
    "Кіборги (2017)"
]

# ---------------------------
# Ініціалізація БД
# ---------------------------
conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS watched_movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_title TEXT,
    watch_date TEXT,
    rating INTEGER,
    notes TEXT
)
""")
conn.commit()

# ---------------------------
# Заголовок
# ---------------------------
st.title("🎬 Особистий щоденник перегляду українських фільмів")
st.subheader("Довженко Топ-100")

# ---------------------------
# Форма додавання перегляду
# ---------------------------
st.header("➕ Додати перегляд")

with st.form("add_movie"):
    movie = st.selectbox("Фільм", DOVZHENKO_TOP_100)
    watch_date = st.date_input("Дата перегляду", date.today())
    rating = st.slider("Оцінка", 1, 10, 7)
    notes = st.text_area("Нотатки")
    submitted = st.form_submit_button("Додати перегляд")

    if submitted:
        cursor.execute(
            "INSERT INTO watched_movies (movie_title, watch_date, rating, notes) VALUES (?, ?, ?, ?)",
            (movie, watch_date.isoformat(), rating, notes)
        )
        conn.commit()
        st.success("Перегляд додано!")

# ---------------------------
# Всі переглянуті фільми
# ---------------------------
st.header("📋 Переглянуті фільми")

df = pd.read_sql_query("SELECT * FROM watched_movies", conn)

if not df.empty:
    st.dataframe(df)
else:
    st.info("Ще немає доданих переглядів.")

# ---------------------------
# Статистика
# ---------------------------
st.header("📊 Статистика переглядів")

if not df.empty:
    df["watch_date"] = pd.to_datetime(df["watch_date"])
    df["month"] = df["watch_date"].dt.to_period("M")

    # ---- Bar chart: перегляди по місяцях
    st.subheader("Кількість переглядів за місяцями")
    monthly = df.groupby("month").size()

    fig1, ax1 = plt.subplots()
    monthly.plot(kind="bar", ax=ax1)
    ax1.set_xlabel("Місяць")
    ax1.set_ylabel("Кількість переглядів")
    st.pyplot(fig1)

    # ---- Pie chart: розподіл оцінок
    st.subheader("Розподіл оцінок")

    def rating_group(r):
        if r <= 3:
            return "1–3"
        elif r <= 6:
            return "4–6"
        elif r <= 8:
            return "7–8"
        else:
            return "9–10"

    df["rating_group"] = df["rating"].apply(rating_group)
    rating_counts = df["rating_group"].value_counts()

    fig2, ax2 = plt.subplots()
    ax2.pie(
        rating_counts,
        labels=rating_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax2.axis("equal")
    st.pyplot(fig2)
else:
    st.info("Додайте хоча б один фільм для перегляду статистики.")

# ---------------------------
# Випадковий фільм
# ---------------------------
st.header("🎲 Випадковий фільм для перегляду")

watched_titles = set(df["movie_title"]) if not df.empty else set()
unwatched = list(set(DOVZHENKO_TOP_100) - watched_titles)

if st.button("Порадити фільм"):
    if unwatched:
        st.success(f"Рекомендуємо переглянути: **{random.choice(unwatched)}**")
    else:
        st.info("Ви вже переглянули всі фільми зі списку 🎉")
