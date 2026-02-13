from django.urls import path
from . import views

urlpatterns = [
    path('', views.resume_builder_view, name='resume_form'),
    path('generate/', views.generate_resume_api, name='generate_resume_api'),
    path('api/resume/generate/', views.generate_resume_api, name='generate_resume'),
    path('preview/', views.preview_resume, name='preview_resume'),
    path('download/', views.download_pdf, name='download_pdf'),

]
