from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category/<slug:category_slug>/', views.start_quiz, name='start_quiz'), 
    path('quiz/<int:session_id>/question/<int:question_num>/', views.quiz_question, name='quiz_question'),
    path('quiz/<int:session_id>/submit/', views.submit_answer, name='submit_answer'),
    path('quiz/result/<int:session_id>/', views.quiz_result, name='quiz_result'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]