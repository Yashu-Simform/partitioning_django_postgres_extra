from django.urls import path
from .views import (
    TodoListView, TodoDetailView, TodoCreateView,
    TodoUpdateView, TodoDeleteView
)

urlpatterns = [
    path("", TodoListView.as_view(), name="todo-list"),
    path("todo/<int:pk>/", TodoDetailView.as_view(), name="todo-detail"),
    path("todo/create/", TodoCreateView.as_view(), name="todo-create"),
    path("todo/<int:pk>/update/", TodoUpdateView.as_view(), name="todo-update"),
    path("todo/<int:pk>/delete/", TodoDeleteView.as_view(), name="todo-delete"),
]
