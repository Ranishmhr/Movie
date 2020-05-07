import numpy
import pandas as pd
import pickle
import pymysql
import os
from django.conf import settings


# connection = pymysql.connect("localhost", "postgres", "Ranish1998", "test")
ratings= pd.read_sql_query("SELECT * from movies_ratings", connection)
movies=pd.read_sql_query("SELECT * from movies_movies", connection)

ratings=pd.merge(movies,ratings).drop(columns=["genres","timestamp"])#["genres","timestamp"],axis=1

user_ratings=ratings.pivot_table(index={'userId_id'},columns={'title'},values={'rating'})
movie_user_rating_pivot=user_ratings


user_ratings=user_ratings.fillna(0)


file_ = open(os.path.join(settings.BASE_DIR, 'testfile'),'rb')
pickle_model = pickle.load(file_)
file_.close()


preds_df = pd.DataFrame(pickle_model, index=user_ratings.index,columns = user_ratings.columns)


def recommend_movies(predictions_df, userID, movies_df, original_ratings_df, num_recommendations=5):
	 # Get and sort the user's predictions
	    user_row_number = userID - 1 # UserID starts at 1, not 0
	    sorted_user_predictions = predictions_df.iloc[user_row_number].sort_values(ascending=False)
	   
	    
	    # Get the user's data and merge in the movie information.
	    user_data = original_ratings_df[original_ratings_df.userId_id == (userID)]
	    user_full = (user_data.merge(movies_df, how = 'left', left_on = 'id', right_on = 'id'))
	 
	    print('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
	    print('Recommending the highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
	    
	    # Recommend the highest predicted rating movies that the user hasn't seen yet.
	    recommendations = (movies_df[~movies_df['id'].isin(user_full['id'])].
	         merge(pd.DataFrame(sorted_user_predictions).reset_index()).
	         rename(columns = {userID: 'Ratings'}).
	         sort_values('Ratings', ascending = False).
	                       iloc[:num_recommendations :1])
	    return user_full, recommendations


already_rated, predictions = recommend_movies(preds_df, request.user.id, movies, ratings, 20)



