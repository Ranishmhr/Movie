from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView
from pandas.tests.groupby.test_value_counts import df

from .models import Movies, Ratings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import numpy as np
import pandas as pd
import pymysql
from django.contrib.auth.decorators import login_required
import pickle
import os
from django.conf import settings

from django.db.models import Avg
from django_pandas.io import read_frame
import psycopg2
from sqlalchemy import create_engine
from accounts.forms import ReviewForm


#
# def recommendation(request):
#     # connection = pymysql.connect("localhost", "postgres", "Ranish1998", "test")
#     # connection = psycopg2.connect(user = "postgres",
#                                   # password = "Ranish1998",
#                                   # host = "localhost",
#                                   # database = "test")
#     engine=create_engine('postgresql://postgres:Ranish1998@localhost:5432/test2')
#
#     # movies=connection.cursor()
#     # ratings=connection.cursor()
#     # movies.execute('SELECT * from movies_movies')
#     # ratings.execute('SELECT * from movies_ratings')
#     # movies = pd.read_sql_query("SELECT * from movies_movies",connection)
#     # ratings = pd.read_sql_query("SELECT * from movies_ratings",connection)
#     # m=Movies.objects.all()
#     # r=Ratings.objects.all()
#
#     movies= pd.read_sql_query('SELECT * from "movies_movies"',engine)
#     ratings=pd.read_sql_query('SELECT * from "movies_ratings"',engine)
#     current_user=request.user.id
#     print("current user=\n",current_user)
#
#     # ratings=pd.merge(movies,ratings).drop(columns=["genres","timestamp"])#["genres","timestamp"],axis=1
#     # ratings=pd.merge(movies,ratings).drop(columns=["genres"])
#     print("Ratingssssssss=\n",ratings)
#
#
#     ratings=pd.merge(movies,ratings)#["genres","timestamp"],axis=1
#
#
#     print("ratingsssssssssssssssssssss=\n",ratings)
#
#     user_ratings=ratings.pivot_table(index={'userid_id'},columns={'title'},values={'rating'})
#     # user_ratings=ratings.pivot_table(index={'userId'},columns={'title'},values={'rating'})
#     movie_user_rating_pivot=user_ratings
#
#
#     user_ratings=user_ratings.fillna(0)
#     print("USER=\n",user_ratings)
#
#
#     file_ = open(os.path.join(settings.BASE_DIR, 'testfile1'),'rb')
#     pickle_model = pickle.load(file_)
#     file_.close()
#     a=25
#     b=3634
#
#
#     preds_df = pd.DataFrame(pickle_model, index=user_ratings.index,columns = user_ratings.columns)
#     # preds_df = pd.DataFrame(pickle_model, a,b)
def recommendation(request):
    # connection = pymysql.connect("localhost", "root", "Ranish1998", "movietwo")

    engine = create_engine('postgresql://postgres:Ranish1998@localhost:5432/test3')
    movies = pd.read_sql_query('SELECT * from "movies_movies"', engine)
    ratings=pd.read_sql_query('SELECT * from "movies_ratings"',engine)


    # movies = pd.read_sql_query("SELECT * from movies_movies",connection)
    # ratings = pd.read_sql_query("SELECT * from movies_ratings",connection)

    current_user=request.user.id
    print(current_user)

    ratings=pd.merge(movies,ratings).drop(columns=["genres","timestamp"])#["genres","timestamp"],axis=1

    print("RATINGSSSSSSSSSSSSSSSSSSSSSSSSS\n",ratings)
    user_ratings=ratings.pivot_table(index={'userId_id'},columns={'title'},values={'rating'})
    movie_user_rating_pivot=user_ratings


    user_ratings=user_ratings.fillna(0)
    print("users\n",user_ratings)

    file_ = open(os.path.join(settings.BASE_DIR, 'testfile'),'rb')
    pickle_model = pickle.load(file_)
    file_.close()


    preds_df = pd.DataFrame(pickle_model, index=user_ratings.index,columns = user_ratings.columns)


    def recommend_movies(predictions_df, userID, movies_df, original_ratings_df, num_recommendations=5):
         # Get and sort the user's predictions
            user_row_number = userID - 1 # UserID starts at 1, not 0

            user_data = original_ratings_df[original_ratings_df.userId_id == (userID)]
            user_full = (user_data.merge(movies_df, how = 'left', left_on = 'movieId_id', right_on = 'movieId_id'))




            # Get the user's data and merge in the movie information.


            print('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
            print('Recommending the highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
            
            # Recommend the highest predicted rating movies that the user hasn't seen yet.
            if user_full.shape[0]>0:
                title="Recommendation"
                sorted_user_predictions = predictions_df.iloc[user_row_number].sort_values(ascending=False)


                recommendations = (movies_df[~movies_df['movieId_id'].isin(user_full['id'])].
                     merge(pd.DataFrame(sorted_user_predictions).reset_index()).
                     rename(columns = {userID: 'Ratings'}).
                     sort_values('Ratings', ascending = False).
                                   iloc[:num_recommendations :1])
            else:
                title="Popular Movies"
                movie_ratings = original_ratings_df.groupby('movieId_id')['rating']
                avg_ratings = movie_ratings.mean()
                avg_ratings=round(avg_ratings, 2)
                num_ratings = movie_ratings.count()


                rating_count_df = pd.DataFrame({'avg_rating': avg_ratings, 'num_ratings': num_ratings})



                movie_recs = movies.set_index('movieId_id').join(rating_count_df)

                recommendations = (movies_df[~movies_df['movieId_id'].isin(user_full['id'])].merge(movie_recs.sort_values(['avg_rating', 'num_ratings'], ascending=False).iloc[:num_recommendations :1]))



            return user_full, recommendations,title


    already_rated, predictions,title = recommend_movies(preds_df,current_user, movies, ratings, 50)
    print(predictions)




    context = {
         "object_list": predictions,
         "title": title
        }

    return render(request, "recommendation.html", context)


def post_list(request):
    query=request.GET.get("title")
    queryset_list=None
    if query:
        queryset_list=Movies.objects.all().filter(title__icontains=query)
        if not queryset_list:
            return render(request, "search.html")
    else:
        queryset_list=Movies.objects.all()
    userid = request.user.id
    userName = request.user.username
    # queryset_list = Ratings.objects.select_related('movieId')
    # queryset_list = Movies.objects.all()
    # queryset_list = Total.objects.select_related('movieId')


    paginator = Paginator(queryset_list, 20)
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:

        queryset = paginator.page(1)
    except EmptyPage:

        queryset = paginator.page(paginator.num_pages)

    context = {
        "user_id": userid,
        "user_name": userName,
        "object_list": queryset,
        "title": "List"}
    return render(request, "home.html", context)


def detail(request,id):
    # connection = pymysql.connect("localhost", "postgres", "Ranish1998", "test")
    # ds = pd.read_sql_query("SELECT * from movies_movies", connection)
    # ratings = pd.read_sql_query("SELECT * from movies_ratings", connection)
    detail = Movies.objects.get(id=id)
    # movie_ratings = ratings.groupby('movieId_id')['rating']
    # avg_ratings = movie_ratings.mean()
    rating = Ratings.objects.filter(movieid=id)
    rating=rating.aggregate(rating=Avg('rating'))


    print("id=",id)
    print("\n detail=",detail)
    print("\n rating=",rating)
    print("userid",request.user.id)
    reviews=Ratings.objects.filter(movieid=id).order_by("comment")
    # results = cb.getFrames(ds)
    # content = cb.recommend(item_id=id, num=5,results=results)
    condition=None
    for review in reviews:
        if request.user.id==review.userid.id:
            print("user has reviewed")
            condition="true"
            break
        else:
            print("not reviewed")
            condition="false"
            
        

    current_user=request.user.id
    context = {
        "detail": detail,
        "rating": rating,
        "reviews":reviews,
        "condition":condition,
        "current_user":current_user
        #     "content":content,
    }
    return render(request, "detail.html", context)


def search(request):
    return render(request, 'search.html')

#edit the review
def edit_review(request,review_id):
    if request.user.is_authenticated:
        # movie=Movies.objects.get(id=movie_id)
        #review
        review=Ratings.objects.get(id=review_id)
        movieid=review.movieid
        movieid1=Movies.objects.get(title=movieid)
        movie_id=movieid1.id
        #check if the reviews by the logged in user
        if request.user==review.userid:
            #grant permission
            if request.method=="POST":
                form=ReviewForm(request.POST,instance=review)
                if form.is_valid():
                    data=form.save(commit=False)
                    if (data.rating > 5) or (data.rating < 0):
                        error="Out of range. Please select rating from 1 to 5."
                        return render(request,'edit_review.html',{"error":error,"form":form})
                    else:
                        data.save()
                        return redirect("movies:detail",movie_id)      
            else:
                form=ReviewForm(instance=review)
            return render(request,"edit_review.html",{"form":form})
        else:
            return redirect("movies:detail",movie_id)
    else:
        return redirect("movies:login")

#delete review
def delete_review(request,review_id):
    if request.user.is_authenticated:
        # movie=Movies.objects.get(id=movie_id)
        #review
        review=Ratings.objects.get(id=review_id)
        movieid=review.movieid
        movieid1=Movies.objects.get(title=movieid)
        movie_id=movieid1.id
        #check if the reviews by the logged in user
        if request.user==review.userid:
            #grant permission to dlete
            review.delete()
        
        return redirect("movies:detail",movie_id)
    else:
        return redirect("movies:login")






