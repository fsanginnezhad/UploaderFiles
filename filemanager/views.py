import os
import shutil
import jdatetime  # type: ignore

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import FileUploadForm, UserEditForm

from .data_names import NAMES

from django.core.paginator import Paginator

from django.http import JsonResponse


# region File Manager
@login_required
def file_upload(request):
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf']
    ALLOWED_EXTENSIONS_ = ['.jpg', '.jpeg', '.png', '.pdf', '.xlsx', '.xls', '.xlsm', '.xlsb', '.xltx', '.xlc']
    _ALLOWED_EXTENSIONS_ = ['.jpg', '.jpeg', '.png', '.pdf', '.xlsx', '.xls', '.xlsm', '.xlsb', '.xltx', '.xlc', 'doc', 'docx']
    valid_files = []
    invalid_files = []
    user_re = str(request.user)
    try:
        user = NAMES[str(request.user)]
    except:
        user = user_re
    user_folder_path = os.path.join(settings.MEDIA_ROOT, request.user.username)
    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file[]')
            if not files:
                messages.error(request, 'هیچ فایلی انتخاب نشده است.')
                return redirect('filemanager:file_upload')
            try:
                for file in files:
                    name, ext = os.path.splitext(file.name)
                    if user_re == 'ghavami':
                        if ext.lower() in ALLOWED_EXTENSIONS_:
                            valid_files.append((file, name, ext))
                        else:
                            invalid_files.append(file.name)
                    elif user_re == 'ebrahimi':
                        if ext.lower() in _ALLOWED_EXTENSIONS_:
                            valid_files.append((file, name, ext))
                        else:
                            invalid_files.append(file.name)
                    else:
                        if ext.lower() in ALLOWED_EXTENSIONS:
                            valid_files.append((file, name, ext))
                        else:
                            invalid_files.append(file.name)
                if not valid_files:
                    messages.error(
                        request,
                        f'هیچ فایلی با فرمت مجاز انتخاب نشده است. فرمت‌های مجاز: '
                        f'{"، ".join(ALLOWED_EXTENSIONS_ if user_re == "ghavami" else ALLOWED_EXTENSIONS)}'
                    )
                    return redirect('filemanager:file_upload')
                for file, name, ext in valid_files:
                    current_time = jdatetime.datetime.now().strftime('%Y-%m-%d')
                    filename = f"{current_time} {name}{ext}"
                    file_path = os.path.join(user_folder_path, filename)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                if valid_files:
                    msg = messages.success(request, f'{len(valid_files)} فایل آپلود شد.')
                if invalid_files:
                    msg = messages.warning(request, f"فایل‌های نامعتبر آپلود نشدند: {', '.join(invalid_files)}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'message': msg})
                else:
                    return redirect('filemanager:file_upload')
            except Exception as e:
                messages.error(request, f'خطا در آپلود فایل: {str(e)}')
                return redirect('filemanager:file_upload')
        else:
            messages.error(request, 'فرمت فایل معتبر نیست. لطفاً فایلی با فرمت‌های jpg، jpeg، png، pdf انتخاب کنید.') # noqa
            return redirect('filemanager:file_upload')
    else:
        form = FileUploadForm()
    return render(request, 'filemanager/file_upload.html', {'form': form, 'user': user, 'user_re': user_re})
# endregion


# region Accounts
def is_admin(user):
    return user.is_superuser


def create_user_folder(username):
    user_folder_path = os.path.join(settings.MEDIA_ROOT, username)
    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)
    return user_folder_path


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not user.is_staff:
                create_user_folder(user.username)
                return redirect('filemanager:file_upload')
            return redirect('filemanager:admin_page')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        if request.user.is_authenticated:
            if not request.user.is_staff:
                return redirect('filemanager:file_upload')
            return redirect('filemanager:admin_page')
    return render(request, 'accounts/login.html')


@user_passes_test(is_admin)
def admin_page(request):
    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        User.objects.create_user(username=new_username, password=new_password)
        messages.success(request, f'User {new_username} created successfully!')
    user_folders = os.listdir(settings.MEDIA_ROOT)
    paginator = Paginator(user_folders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'accounts/admin_page.html',
        {
            'page_obj': page_obj
        }
    )


@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounts/user_list.html', {'page_obj': page_obj})


@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'کابر با موفقیت حذف شد.')
    return redirect('filemanager:user_list')


@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'کاربر با موفقیت ویرایش شد.')
            return redirect('filemanager:user_list')
    else:
        form = UserEditForm(instance=user)
        form.fields['is_admin'].initial = user.is_superuser
        form.fields['is_active'].initial = user.is_active
    return render(request, 'accounts/edit_user.html', {'form': form, 'user': user})


@user_passes_test(is_admin)
def user_page(request):
    user = request.user.username
    user_folder_path = create_user_folder(user)
    user_files = os.listdir(user_folder_path)
    return render(
        request,
        'accounts/user_page.html',
        {
            'user_files': user_files,
            'username': user
        }
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('filemanager:file_upload')


@user_passes_test(is_admin)
def delete_file(request, username, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, username, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        messages.success(request, f'File {filename} deleted successfully!')
    else:
        messages.error(request, 'File does not exist.')
    return redirect('filemanager:admin_page')


@user_passes_test(is_admin)
def admin_manage_photos(request):
    users = [
        d for d in os.listdir(settings.MEDIA_ROOT)
        if os.path.isdir(os.path.join(settings.MEDIA_ROOT, d))
    ]
    selected_user_photos = {}
    selected_user = request.GET.get('user')
    if selected_user:
        user_folder_path = os.path.join(settings.MEDIA_ROOT, selected_user)
        if os.path.exists(user_folder_path):
            selected_user_photos = {
                selected_user: os.listdir(user_folder_path)
            }
    if request.method == 'POST':
        selected_photos_to_delete = request.POST.getlist('photos_to_delete')
        folder_to_delete = request.POST.get('folder_to_delete')
        if selected_photos_to_delete:
            for photo in selected_photos_to_delete:
                photo_path = os.path.join(settings.MEDIA_ROOT, photo)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                    messages.success(
                        request,
                        f"Photo {photo} deleted successfully."
                    )
                else:
                    messages.error(request, f"Photo {photo} not found.")
        elif folder_to_delete:
            folder_path = os.path.join(settings.MEDIA_ROOT, folder_to_delete)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                messages.success(
                    request,
                    f"Folder for user {folder_to_delete} deleted successfully."
                )
            else:
                messages.error(request, "Folder not found.")
        return redirect('filemanager:admin_manage_photos')
    return render(
        request,
        'accounts/admin_manage_photos.html',
        {
            'users': users,
            'selected_user_photos': selected_user_photos,
            'selected_user': selected_user,
        }
    )
# endregion
