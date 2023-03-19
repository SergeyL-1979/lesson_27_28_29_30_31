from django.contrib import admin
from django.urls import path

# from vacancies import views
from vacancies import views

urlpatterns = [
    path('', views.VacancyListView.as_view(), name='Вакансии'),
    path('<int:pk>/', views.VacancyDetailView.as_view(), name='Детали'),
    path('create/', views.VacancyCreateView.as_view(), name='Создание'),
    path('update/<int:pk>/', views.VacancyUpdateView.as_view(), name='Редактирование'),
    path('delete/<int:pk>/', views.VacancyDeleteView.as_view(), name='Удаление'),
    path('by_user/', views.UserVacancyDetailView.as_view(), name='Подсчет пользователей'),
]