from django.shortcuts import render
import os
import mimetypes
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from .models import VKGROUPREQUESTS, VKGROUP
from .forms import VkRequestForm
from .vk_wall_get import *

def home(request):
    form = VkRequestForm()
    return render(request, 'vk_create_request/home.html', {'form': form})

def vk_rusult(request):
    if request.method == "POST":
        form = VkRequestForm(request.POST)
        if form.is_valid():
            id_group = form.cleaned_data['id_group']
            count_posts = form.cleaned_data['count_posts']
            filter_posts = form.cleaned_data['filter_posts']
            data = main_vk_request_wall(id_group, count_posts, filter_posts)
            vk_excel_url = data['vk_excel_url']
            vk_req = VKGROUPREQUESTS(id_group=id_group, count_posts=count_posts, file_path=vk_excel_url)
            vk_req.save()
            return render(request, 'vk_create_request/result.html', {'id_group': id_group, 'counts_posts': count_posts,
                                                                     'vk_excel_url': vk_excel_url})

def download_xlsx(request):
    file_path = request.path
    file_name = os.path.basename(file_path)
    response = HttpResponse(FileWrapper(open(file_path)), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' %file_name
    response['Content-Length'] = os.path.getsize(file_path)
    return response