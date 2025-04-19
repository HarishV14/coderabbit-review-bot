import json

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, FormView, TemplateView, UpdateView
from django_filters.views import FilterView

from app.domain.assets import (
    create_assets_in_bulk,
)
from app.filters import AssetsFilter
from app.forms.asset import AssetStatusUpdateForm, BulkAssetForm
from app.models import Asset, FileType, UploadedFile


class AssetsListView(PermissionRequiredMixin, FilterView):
    model = Asset
    template_name = "assets/all/index.html"
    context_object_name = "assets_list"
    filterset_class = AssetsFilter
    permission_required = "app.view_asset"
    paginate_by = 20


class UnusedAssetsListView(PermissionRequiredMixin, FilterView):
    model = Asset
    template_name = "assets/unused/index.html"
    context_object_name = "unused_assets_list"
    filterset_class = AssetsFilter
    permission_required = "app.view_asset"
    paginate_by = 20
    queryset = Asset.objects.filter(contents__isnull=True)


class TranscodingAssetsListView(PermissionRequiredMixin, FilterView):
    model = Asset
    template_name = "assets/transcoding/index.html"
    context_object_name = "transcoding_assets_list"
    filterset_class = AssetsFilter
    permission_required = "app.view_asset"
    paginate_by = 20

    def get_queryset(self):
        return Asset.objects.filter(
            status__in=[
                Asset.Status.QUEUED,
                Asset.Status.TRANSCODING,
                Asset.Status.ERROR,
            ],
            category__in=[
                Asset.Category.VIDEO,
                Asset.Category.AUDIO,
                Asset.Category.LIVE_STREAM,
            ],
        )


class AssetsExplorerView(PermissionRequiredMixin, FilterView):
    model = Asset
    template_name = "assets/file_explorer/index.html"
    context_object_name = "assets_list"
    filterset_class = AssetsFilter
    permission_required = "app.view_asset"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.parent = None
        parent_id = request.GET.get("parent")
        if parent_id:
            self.parent = get_object_or_404(
                Asset.objects.filter(category=Asset.Category.FOLDER, id=parent_id),
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Asset.objects.filter(parent=self.parent)
            .order_by("-created")
            .sort_folders_first()
        )


class BulkAssetCreateView(PermissionRequiredMixin, FormView):
    permission_required = "app.add_asset"
    form_class = BulkAssetForm

    def form_valid(self, form):
        assets = create_assets_in_bulk(**form.cleaned_data, user=self.request.user)
        return JsonResponse(
            {
                "status": "success",
                "assets": json.loads(serializers.serialize("json", assets)),
            },
            status=201,
        )

    def form_invalid(self, form):
        errors = form.errors.get("errors", [])
        return JsonResponse({"status": "error", "errors": errors}, status=400)

    def post(self, request, *args, **kwargs):
        if request.content_type != "application/json":
            return JsonResponse(
                {"status": "error", "message": "Invalid content type. Expected JSON"},
                status=400,
            )

        form = self.get_form()
        form.data = {"assets": json.loads(request.body)}

        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class AssetStatusUpdateView(PermissionRequiredMixin, UpdateView):
    model = Asset
    permission_required = "app.change_asset"
    form_class = AssetStatusUpdateForm

    def get_object(self, queryset=None):
        return get_object_or_404(Asset, id=self.kwargs["pk"])

    def form_valid(self, form):
        asset = form.save()

        return JsonResponse(
            {
                "status": "success",
                "asset_id": asset.id,
                "message": "Asset status updated",
            },
            status=200,
        )

    def form_invalid(self, form):
        return JsonResponse({"status": "error", "message": form.errors}, status=400)


class AssetsUploadView(TemplateView):
    template_name = "assets/bulk_upload/index.html"


class VideoAssetDetailView(PermissionRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/video_detail/index.html"
    context_object_name = "video_asset"
    permission_required = "app.view_asset"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(category=Asset.Category.VIDEO)
            .select_related("uploaded_file", "video")
            .prefetch_related("contents")
        )


class AudioAssetDetailView(PermissionRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/audio_detail/index.html"
    context_object_name = "audio_asset"
    permission_required = "app.view_asset"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(category=Asset.Category.AUDIO)
            .select_related("uploaded_file", "audio")
            .prefetch_related("contents")
        )


class EbookAssetDetailView(PermissionRequiredMixin, DetailView):
    model = Asset
    template_name = "assets/ebook_detail/index.html"
    context_object_name = "ebook_asset"
    permission_required = "app.view_asset"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(category=Asset.Category.EBOOK)
            .select_related("uploaded_file")
            .prefetch_related("contents")
        )


class EbookReaderView(PermissionRequiredMixin, DetailView):
    model = UploadedFile
    context_object_name = "ebook"
    template_name = "ebook_reader/index.html"
    permission_required = "app.view_asset"

    def get_queryset(self):
        return super().get_queryset().filter(file_type=FileType.DOCUMENT)
