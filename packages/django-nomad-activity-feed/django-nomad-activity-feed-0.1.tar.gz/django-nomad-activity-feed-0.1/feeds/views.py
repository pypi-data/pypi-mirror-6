from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required


@login_required
def follow(request, content_type_id, object_id):
    if request.method == 'POST' and request.is_ajax():
        content_type = get_object_or_404(ContentType, pk=content_type_id)
        model = content_type.model_class()
        obj = get_object_or_404(model, pk=object_id)

        request.user.follow(obj)

        return HttpResponse('success')
    else:
        raise Http404


@login_required
def unfollow(request, content_type_id, object_id):
    if request.method == 'POST' and request.is_ajax():
        content_type = get_object_or_404(ContentType, pk=content_type_id)
        model = content_type.model_class()
        obj = get_object_or_404(model, pk=object_id)

        request.user.unfollow(obj)

        return HttpResponse('success')
    else:
        raise Http404
