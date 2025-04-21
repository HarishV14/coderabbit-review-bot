from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app.forms.content import ContentImageForm
from app.models import Content, ContentImage
from app.utils.htmx import HTTPResponseHXRedirect


def create_content_image(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    form = ContentImageForm(request.POST or None)
    if form.is_valid():
        content_image = form.save(commit=False)
        content_image.content = content
        content_image.save()
        messages.success(
            request,
            f"{content_image.get_image_type_display()} added successfully!",
        )
        return HTTPResponseHXRedirect(request.GET.get("redirect_to"))
    return render(
        request,
        "partials/create_content_image.html",
        {"form": form, "content": content},
    )


def update_content_image(request, pk):
    content_image = get_object_or_404(ContentImage, id=pk)
    form = ContentImageForm(request.POST or None, instance=content_image)
    if form.is_valid():
        form.save()
        messages.success(
            request,
            f"{content_image.get_image_type_display()} updated successfully!",
        )
        return HTTPResponseHXRedirect(request.GET.get("redirect_to"))
    return render(
        request,
        "partials/update_content_image.html",
        {"form": form, "content_image": content_image},
    )


@require_POST
def delete_content_image(request, pk):
    content_image = get_object_or_404(ContentImage, id=pk)
    content_image.delete()
    messages.success(
        request,
        f"{content_image.get_image_type_display()} deleted successfully!",
    )
    return redirect(request.GET.get("redirect_to"))
