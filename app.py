import streamlit as st
import pickle
import requests
import time

# ============================
# TMDB API KEY
# ============================
API_KEY = "6142ff982669ff4ffc9171222f7bfe21"

# ============================
# Load Movie Data
# ============================
with open("movie_data.pkl", "rb") as file:
    movies, cosine_sim = pickle.load(file)

# ============================
# Request Session
# ============================
session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

# ============================
# Fetch Movie Poster
# ============================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }

    for _ in range(3):

        try:

            response = session.get(
                url,
                params=params,
                timeout=20
            )

            if response.status_code == 200:

                data = response.json()

                poster_path = data.get("poster_path")

                if poster_path:
                    return "https://image.tmdb.org/t/p/w500" + poster_path

            elif response.status_code == 401:
                print("Invalid API Key")
                break

            elif response.status_code == 404:
                print(f"Movie {movie_id} not found")
                break

            elif response.status_code == 429:
                print("Too many requests...")
                time.sleep(2)

        except Exception as e:
            print(e)

        time.sleep(1)

    return "https://dummyimage.com/500x750/000/fff&text=No+Poster"

# ============================
# Recommend Movies
# ============================
def recommend(movie):

    movie_index = movies[movies["title"] == movie].index[0]

    distances = cosine_sim[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    recommended_names = []
    recommended_posters = []

    for item in movie_list:

        movie_id = movies.iloc[item[0]].movie_id
        title = movies.iloc[item[0]].title

        recommended_names.append(title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_names, recommended_posters

# ============================
# Streamlit UI
# ============================
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox(
    "Select a Movie",
    movies["title"].values
)

if st.button("Recommend"):

    with st.spinner("Finding similar movies..."):

        names, posters = recommend(selected_movie)

    st.success("Recommendations")

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.write(names[i])

    cols = st.columns(5)

    for i in range(5, 10):
        with cols[i - 5]:
            st.image(posters[i], use_container_width=True)
            st.write(names[i])