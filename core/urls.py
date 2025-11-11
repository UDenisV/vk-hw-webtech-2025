from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('questions/<int:id>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('tag/<str:title>/', views.TagView.as_view(), name='tag_page'),
    path('ask/', views.AskQuestionView.as_view(), name='ask_question'),
    path('settings/', views.UserSettingsView.as_view(), name='user_settings'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.logout_view, name='logout_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)