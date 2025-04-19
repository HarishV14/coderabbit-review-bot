from http import HTTPStatus

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from app.models import UploadedFile


@require_POST
def upload_file(request):
    try:
        file = request.FILES["file"]
        uploaded_file = UploadedFile(file=file)
        uploaded_file.save()

        return JsonResponse(
            {
                "message": "File uploaded and saved successfully",
                "id": uploaded_file.id,
                "file_url": uploaded_file.file.url,
            },
            status=HTTPStatus.CREATED,
        )
    except Exception as e:  # noqa: BLE001
        return JsonResponse(
            {"error": f"{e!s}"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
