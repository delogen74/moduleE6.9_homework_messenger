from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Chat, Message
from .forms import ProfileEditForm, UserRegistrationForm
from rest_framework import viewsets, permissions
from .serializers import ChatSerializer, MessageSerializer
from django.http import Http404, JsonResponse


# Главная страница
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# Дашборд для авторизованных пользователей
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# Список всех пользователей
@login_required
def users_list(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'users.html', {'users': users})


# Комната чата
@login_required
def chat_room(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    messages = Message.objects.filter(chat=chat)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/messages.html', {'messages': messages})

    return render(request, 'chat.html', {'chat': chat, 'messages': messages})

# Список чатов текущего пользователя
@login_required
def chat_list(request):
    chats = Chat.objects.filter(members=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Возвращаем частичный шаблон для AJAX-запросов
        return render(request, 'partials/chats.html', {'chats': chats})

    return render(request, 'chats.html', {'chats': chats})


@login_required
def create_chat(request):
    if request.method == "POST":
        user1 = request.user
        members_ids = request.POST.getlist('members')  # Список ID участников
        chat_name = request.POST.get('chat_name', 'Групповой чат')

        # Если это личный чат (два участника), проверяем на дубликаты
        if len(members_ids) == 1:
            user2_id = members_ids[0]
            user2 = get_object_or_404(CustomUser, id=user2_id)

            # Проверяем на существование личного чата
            existing_chat = Chat.objects.filter(
                members=user1
            ).filter(
                members=user2
            ).distinct()

            if existing_chat.exists() and existing_chat.first().members.count() == 2:
                # Перенаправляем на существующий личный чат
                return redirect('chat_room', chat_id=existing_chat.first().id)

            # Если личного чата нет, создаём новый
            new_chat = Chat.objects.create(name=f"Чат с {user2.username}")
            new_chat.members.add(user1, user2)
            return redirect('chat_room', chat_id=new_chat.id)

        # Групповой чат: создаём новый чат независимо от участников
        new_chat = Chat.objects.create(name=chat_name)
        new_chat.members.add(user1, *members_ids)
        return redirect('chat_room', chat_id=new_chat.id)

    # Для GET-запроса показываем форму для создания чата
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'create_chat.html', {'users': users})





# Редактирование профиля
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


# Страница профиля
@login_required
def profile(request):
    form = ProfileEditForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('dashboard')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ограничиваем доступ к чатам, в которых состоит пользователь
        return self.queryset.filter(members=self.request.user)

    def perform_create(self, serializer):
        # При создании чата добавляем текущего пользователя как участника
        chat = serializer.save()
        chat.members.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ограничиваем доступ к сообщениям из чатов, где пользователь является участником
        return self.queryset.filter(chat__members=self.request.user)

    def perform_create(self, serializer):
        # Устанавливаем отправителя сообщения текущим пользователем
        serializer.save(sender=self.request.user)

@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Проверяем, что пользователь является участником чата
    if request.user in chat.members.all():
        chat.delete()
        messages.success(request, "Чат успешно удален.")
    else:
        messages.error(request, "У вас нет прав для удаления этого чата.")

    return redirect('chat_list')