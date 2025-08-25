from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import TodoNonExisting, Todo
from todo.services.todo_list import get_partitioned_todos
from django.db.models import Q
from datetime import datetime, timedelta

class TodoListView(ListView):
    model = TodoNonExisting
    template_name = "todos/todo_list.html"
    context_object_name = "todos"
    ordering = ["-created_at"]
    paginate_by = 50

    def get_queryset(self):
        # Default: last 3 months of partitioned data
        queryset = TodoNonExisting.objects.all()

        # --- Search filter ---
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        # --- Completion status filter ---
        status = self.request.GET.get("status")
        if status == "completed":
            queryset = queryset.filter(is_completed=True)
        elif status == "pending":
            queryset = queryset.filter(is_completed=False)

        # --- Date filter ---
        date_filter = self.request.GET.get("date")
        today = datetime.now().date()

        if date_filter == "7days":
            queryset = queryset.filter(created_at__gte=today - timedelta(days=7))
        elif date_filter == "30days":
            queryset = queryset.filter(created_at__gte=today - timedelta(days=30))
        elif date_filter == "90days":
            queryset = queryset.filter(created_at__gte=today - timedelta(days=90))

        return queryset

class TodoDetailView(DetailView):
    model = TodoNonExisting
    template_name = "todos/todo_detail.html"
    context_object_name = "todo"

class TodoCreateView(CreateView):
    model = TodoNonExisting
    fields = ["title", "description", "is_completed"]
    template_name = "todos/todo_form.html"
    success_url = reverse_lazy("todo-list")

class TodoUpdateView(UpdateView):
    model = TodoNonExisting
    fields = ["title", "description", "is_completed"]
    template_name = "todos/todo_form.html"
    success_url = reverse_lazy("todo-list")

class TodoDeleteView(DeleteView):
    model = TodoNonExisting
    template_name = "todos/todo_confirm_delete.html"
    success_url = reverse_lazy("todo-list")
