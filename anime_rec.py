import pandas as pd
from surprise.model_selection import cross_validate
from surprise.prediction_algorithms import SVD
from surprise.prediction_algorithms import KNNWithMeans, KNNBasic, KNNBaseline
from surprise.model_selection import GridSearchCV
import numpy as np
import time
import pickle
from surprise import Reader, Dataset
from surprise.prediction_algorithms import knns
# from surprise.similarities import cosine, msd, pearson
from surprise import accuracy
import streamlit as st

df = pd.read_csv('csv_files/anime_data.csv')
df = df.drop('Unnamed: 0', axis = 1)
pd.options.display.max_colwidth = 1000
rec_df = df.drop(columns = df[['title', 'genres', 'type']])
rec_df = rec_df[['User_ID', 'Title_ID', 'ratings']]
rec_match = df[['title', 'Title_ID', 'genres']].drop_duplicates('Title_ID')


reader = Reader(rating_scale = (1,10))
data = Dataset.load_from_df(rec_df, reader)

with open('svd.pickle', 'rb') as f:
    svd = pickle.load(f)


def get_recommendations(user_ratings, num_recs, genre):
    new_ratings_df = rec_match.append(user_ratings,ignore_index=True)
    new_ratings_df = new_ratings_df[new_ratings_df.genres.str.contains(genre, na=False)]
    new_ratings_df = new_ratings_df.drop(columns=['title', 'genres'])

#     #load in new df
    new_data = Dataset.load_from_df(new_ratings_df,reader)
#     #create new svd object
    # svd_new = SVD()
#     #re fit the model
    svd(new_data.build_full_trainset())

#     # make predictions for the user
    list_of_animes = []
    for a_id in new_ratings_df['Title_ID'].unique():
        list_of_animes.append((a_id, svd.predict(new_ratings_df['User_ID'].max(),a_id)[3]))

    # order the predictions from highest to lowest rated
    ranked_animes = sorted(list_of_animes, key=lambda x:x[1], reverse=True, sort = 'False')

    rec_num = 1
    for i in ranked_animes[:num_recs]:
        recommended = rec_match[rec_match['Title_ID'] == i[0]]
        st.write('Recommendation number:', rec_num)
        st.write('Anime: ' + recommended.values[0][0])
        st.write('Genres: ' + (recommended.values[0][2]))
        st.write('Type' + recommended.values[0][-1])
        # print('\n')
        rec_num +=1
    st.write("Thank You For Using John And Paul's Anim-endation")

def anime_rater(df, num):
    userID = rec_df.User_ID.max()+1
    num_recs = st.slider(label = 'How many recommendations would you like? Please enter a number from 1 to 10:', 
                            min_value = 0, max_value = 10)
    genre = st.text_input('Please enter your favorite genre. ').title()
    rating_list = []
    
    while num > 0:
        anime = df[df['genres'].str.contains(genre)].sample(1)
        st.write('\nPlease rate the following {} Animes. \n'.format(num))
        st.write('Anime: ' + str(anime.values[0][0]))
        st.write('Genre: ' + str(anime.values[0][1]))
        st.write('Type: ' + str(anime.values[0][3]))
        
        rating = st.slider(label = 'How do you rate this Anime on a scale of 1-10, press 0 if you are never watched this anime. :', 
                                    min_value = 0, max_value = 10)
            
        if rating == 0 :
            continue
        
        if rating > 10:
            st.write('Rating must be below 10!')
            continue
            
        if rating < 1:
            st.write('Rating must be above 0!')
            continue
        
        else:
            rating_one_anime = {'User_ID':userID,'Title_ID': anime['Title_ID'].values[0],'rating': int(rating)}
            rating_list.append(rating_one_anime) 
            num -= 1
        time.sleep(.5)
    st.write('\n'+'-----Making Recommendations-----'+'\n')
    time.sleep(1)
    get_recommendations(rating_list, int(num_recs), genre)


st.write(anime_rater(df,5))
    