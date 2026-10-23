"""File upload validation for DAS Document models.

Enforces an extension whitelist, a size ceiling, and a compression/archive
policy on user-uploaded files, so a save() can never persist an unexpected
file type (executables, scripts, disguised binaries) or an unsafe/nested
archive.
"""
import logging
import os
import uuid
import zipfile

from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

DEFAULT_STANDARD_ALLOWED_EXTENSIONS = frozenset({
    ".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx",
    ".xls", ".xlsx", ".csv", ".txt", ".msg", ".eml",
})

# Backward-compatible alias; existing callers (e.g. ProposalMapDocument's
# explicit archive-union allowed_extensions) keep referring to the static default.
STANDARD_ALLOWED_EXTENSIONS = DEFAULT_STANDARD_ALLOWED_EXTENSIONS

DEFAULT_GIS_ARCHIVE_ALLOWED_EXTENSIONS = frozenset({
    ".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".cpg", ".qix", ".xml",
    ".geojson", ".json", ".gpkg",
})

# Backward-compatible alias; existing callers (e.g. ProposalMapDocument's
# explicit archive-union allowed_extensions) keep referring to the static default.
GIS_ARCHIVE_ALLOWED_EXTENSIONS = DEFAULT_GIS_ARCHIVE_ALLOWED_EXTENSIONS

COMPRESSED_EXTENSIONS = frozenset({".zip"})

DEFAULT_MAX_UPLOAD_SIZE = getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 15 * 1024 * 1024)

# Defence in depth against zip/decompression bombs; not part of the literal
# whitelist spec but a direct consequence of parsing attacker-controlled zips.
MAX_ARCHIVE_UNCOMPRESSED_SIZE = 100 * 1024 * 1024  # 100 MB

# Keys used to look up the dynamic whitelists in GlobalSettings.
GLOBAL_SETTINGS_ALLOWED_EXTENSIONS_KEY = "allowed_file_extensions"
GLOBAL_SETTINGS_ALLOWED_GIS_ARCHIVE_EXTENSIONS_KEY = "allowed_gis_archive_extensions"
GLOBAL_SETTINGS_MAX_UPLOAD_SIZE_MB_KEY = "max_file_upload_size_mb"
GLOBAL_SETTINGS_MAX_UPLOAD_SIZE_MB_INTERNAL_KEY = "max_file_upload_size_mb_internal"


def _parse_extensions(raw):
    """Parse a comma- or space-separated string of extensions into a normalized frozenset.

    e.g. "pdf, png webp" -> frozenset({".pdf", ".png", ".webp"}). Returns None
    if `raw` is empty or contains no usable extensions.
    """
    if not raw:
        return None
    tokens = raw.replace(",", " ").split()
    parsed = {"." + token.strip().lstrip(".").lower() for token in tokens if token.strip()}
    return frozenset(parsed) if parsed else None


def get_standard_allowed_extensions():
    """Resolve the standard extension whitelist dynamically, without requiring a code change.

    Resolution order:
      1. `GlobalSettings` DB row keyed on `allowed_file_extensions` (admin-editable).
      2. `settings.ALLOWED_FILE_EXTENSIONS` (string or iterable of extensions).
      3. `DEFAULT_STANDARD_ALLOWED_EXTENSIONS` (hardcoded fallback).

    Any failure (missing table during migrations/tests, DB not ready, bad
    config value, etc.) is swallowed and resolution falls through to the
    next source, so this function can never itself break a save().
    """
    try:
        from disturbance.components.main.models import GlobalSettings  # local import: avoids circular import with main.models

        row = GlobalSettings.objects.filter(key=GLOBAL_SETTINGS_ALLOWED_EXTENSIONS_KEY).first()
        if row is not None:
            parsed = _parse_extensions(row.value)
            if parsed:
                return parsed
    except Exception:
        logger.exception("Unable to resolve allowed file extensions from GlobalSettings; falling back.")

    try:
        configured = getattr(settings, "ALLOWED_FILE_EXTENSIONS", None)
        if configured:
            if isinstance(configured, str):
                parsed = _parse_extensions(configured)
            else:
                parsed = frozenset("." + str(item).strip().lstrip(".").lower() for item in configured)
            if parsed:
                return parsed
    except Exception:
        logger.exception("Unable to resolve allowed file extensions from Django settings; falling back.")

    return DEFAULT_STANDARD_ALLOWED_EXTENSIONS


def get_gis_archive_allowed_extensions():
    """Resolve the GIS archive inner-file extension whitelist dynamically, without requiring a code change.

    Resolution order:
      1. `GlobalSettings` DB row keyed on `allowed_gis_archive_extensions` (admin-editable).
      2. `settings.ALLOWED_GIS_ARCHIVE_EXTENSIONS` (string or iterable of extensions).
      3. `DEFAULT_GIS_ARCHIVE_ALLOWED_EXTENSIONS` (hardcoded fallback).

    Any failure (missing table during migrations/tests, DB not ready, bad
    config value, etc.) is swallowed and resolution falls through to the
    next source, so this function can never itself break a save().
    """
    try:
        from disturbance.components.main.models import GlobalSettings  # local import: avoids circular import with main.models

        row = GlobalSettings.objects.filter(key=GLOBAL_SETTINGS_ALLOWED_GIS_ARCHIVE_EXTENSIONS_KEY).first()
        if row is not None:
            parsed = _parse_extensions(row.value)
            if parsed:
                return parsed
    except Exception:
        logger.exception("Unable to resolve allowed GIS archive extensions from GlobalSettings; falling back.")

    try:
        configured = getattr(settings, "ALLOWED_GIS_ARCHIVE_EXTENSIONS", None)
        if configured:
            if isinstance(configured, str):
                parsed = _parse_extensions(configured)
            else:
                parsed = frozenset("." + str(item).strip().lstrip(".").lower() for item in configured)
            if parsed:
                return parsed
    except Exception:
        logger.exception("Unable to resolve allowed GIS archive extensions from Django settings; falling back.")

    return DEFAULT_GIS_ARCHIVE_ALLOWED_EXTENSIONS


def get_max_upload_size_bytes(is_internal=False):
    """Resolve the maximum upload size (in bytes) dynamically, without requiring a code change.

    Resolution order (is_internal=True):
      1. `GlobalSettings` DB row keyed on `max_file_upload_size_mb_internal` (admin-editable, value in MB).
      2. Falls back to the external (is_internal=False) resolution below if missing/invalid.

    Resolution order (is_internal=False, the default):
      1. `GlobalSettings` DB row keyed on `max_file_upload_size_mb` (admin-editable, value in MB).
      2. `settings.FILE_UPLOAD_MAX_MEMORY_SIZE` (bytes; default 15728640 / 15 MB).

    Any failure (missing table during migrations/tests, DB not ready, bad
    config value, etc.) is swallowed and resolution falls through to the
    next source, so this function can never itself break a save().
    """
    if is_internal:
        try:
            from disturbance.components.main.models import GlobalSettings  # local import: avoids circular import with main.models

            row = GlobalSettings.objects.filter(key=GLOBAL_SETTINGS_MAX_UPLOAD_SIZE_MB_INTERNAL_KEY).first()
            if row is not None:
                mb_value = float(row.value)
                if mb_value > 0:
                    return int(mb_value * 1024 * 1024)
        except Exception:
            logger.exception("Unable to resolve internal max upload size from GlobalSettings; falling back.")
        return get_max_upload_size_bytes(is_internal=False)

    try:
        from disturbance.components.main.models import GlobalSettings  # local import: avoids circular import with main.models

        row = GlobalSettings.objects.filter(key=GLOBAL_SETTINGS_MAX_UPLOAD_SIZE_MB_KEY).first()
        if row is not None:
            mb_value = float(row.value)
            if mb_value > 0:
                return int(mb_value * 1024 * 1024)
    except Exception:
        logger.exception("Unable to resolve max upload size from GlobalSettings; falling back.")

    return getattr(settings, "FILE_UPLOAD_MAX_MEMORY_SIZE", 15728640)


def validate_uploaded_file(
    file_obj,
    allowed_extensions=None,
    allow_compressed=False,
    max_upload_size=None,
    is_internal=False,
):
    """Validate a single uploaded file object against the DAS whitelist policy.

    `file_obj` is anything exposing `.name` and `.size`/file-like read/seek
    (a Django `UploadedFile`, `FieldFile`, or `ContentFile`). Raises
    `django.core.exceptions.ValidationError` on any violation; returns None
    (no value) when the file is acceptable.

    `allowed_extensions=None` (the default) resolves the whitelist dynamically
    via `get_standard_allowed_extensions()`; pass an explicit set to override.

    `max_upload_size=None` (the default) resolves the byte limit dynamically
    via `get_max_upload_size_bytes(is_internal=is_internal)`; pass an explicit
    integer to override. `is_internal=True` resolves the higher internal-user
    limit instead of the external/default limit.
    """
    if allowed_extensions is None:
        allowed_extensions = get_standard_allowed_extensions()
    if max_upload_size is None:
        max_upload_size = get_max_upload_size_bytes(is_internal=is_internal)

    name = getattr(file_obj, "name", "") or ""
    ext = os.path.splitext(name)[1].lower()

    size = getattr(file_obj, "size", None)
    if size is not None and size > max_upload_size:
        size_mb = size / (1024 * 1024)
        max_mb = max_upload_size / (1024 * 1024)
        raise ValidationError(
            f"File '{name}' ({size_mb:.2f} MB) exceeds the maximum allowed size "
            f"of {max_mb:.2f} MB."
        )

    if ext in COMPRESSED_EXTENSIONS:
        if not allow_compressed:
            raise ValidationError(
                f"Compressed/archive files ('{ext}') are not permitted for this document type."
            )
        _validate_archive(file_obj, name)
        return

    if ext not in allowed_extensions:
        raise ValidationError(
            f"File extension '{ext}' is not permitted. "
            f"Allowed extensions: {', '.join(sorted(allowed_extensions))}."
        )


def _validate_archive(file_obj, name):
    try:
        file_obj.seek(0)
    except (AttributeError, ValueError):
        pass

    gis_archive_allowed_extensions = get_gis_archive_allowed_extensions()

    try:
        with zipfile.ZipFile(file_obj) as archive:
            total_uncompressed = 0
            for info in archive.infolist():
                if info.is_dir():
                    continue
                member_path = info.filename.strip("/")
                member_ext = os.path.splitext(member_path)[1].lower()

                if member_ext in COMPRESSED_EXTENSIONS:
                    raise ValidationError(
                        f"Nested archive '{member_path}' inside '{name}' is not allowed "
                        f"(recursive/nested archives are forbidden)."
                    )
                if "/" in member_path:
                    raise ValidationError(
                        f"Archive '{name}' contains a nested folder ('{member_path}'); "
                        f"only a flat (depth 1) file listing is allowed."
                    )
                if member_ext not in gis_archive_allowed_extensions:
                    raise ValidationError(
                        f"Archive '{name}' contains a disallowed file '{member_path}' "
                        f"(extension '{member_ext}')."
                    )

                total_uncompressed += info.file_size
                if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_SIZE:
                    raise ValidationError(
                        f"Archive '{name}' exceeds the maximum allowed uncompressed size "
                        f"of {MAX_ARCHIVE_UNCOMPRESSED_SIZE} bytes."
                    )
    except zipfile.BadZipFile:
        raise ValidationError(f"'{name}' is not a valid zip archive.")
    finally:
        try:
            file_obj.seek(0)
        except (AttributeError, ValueError):
            pass


class SanitiseFileMixin:
    """Model mixin enforcing the DAS file whitelist/compression policy on save()/clean().

    Must be a leftmost base class ahead of models.Model, e.g.:
        class ApprovalDocument(SanitiseFileMixin, Document):
            ...

    Class-level configuration (declared on the concrete model):
        sanitise_file_field: name of the FileField attribute to validate
            (default "_file", matching the DAS Document convention).
        allowed_extensions: whitelist of standard extensions; if left as
            None (the default), resolved dynamically per-save via
            get_standard_allowed_extensions(). Set explicitly on a model
            (e.g. ProposalMapDocument) to override the dynamic whitelist.
        allow_compressed: whether a .zip archive is accepted at all
            (default False).
        max_upload_size: max bytes accepted; if left as None (the default),
            resolved dynamically per-save via get_max_upload_size_bytes().
            Set explicitly on a model to override the dynamic limit.
        is_internal: whether this Document belongs to an internal-only
            (DBCA staff) upload flow; resolves the internal size limit
            instead of the external/default one (default False).

    New uploads use a model-prefixed UUID filename with the original extension.
    Files already committed to storage retain their paths on subsequent saves.
    """

    sanitise_file_field = "_file"
    allowed_extensions = None
    allow_compressed = False
    max_upload_size = None
    is_internal = False

    def _validate_sanitised_file(self):
        file_obj = getattr(self, self.sanitise_file_field, None)
        if not file_obj:
            return
        validate_uploaded_file(
            file_obj,
            allowed_extensions=self.allowed_extensions,
            allow_compressed=self.allow_compressed,
            max_upload_size=self.max_upload_size,
            is_internal=getattr(self, 'is_internal', False),
        )

    def clean(self):
        super_clean = getattr(super(), "clean", None)
        if callable(super_clean):
            super_clean()
        self._validate_sanitised_file()

    def save(self, *args, **kwargs):
        self._validate_sanitised_file()
        file_field = getattr(self, self.sanitise_file_field, None)
        if file_field and not file_field._committed:
            model_name = self._meta.model_name
            extension = os.path.splitext(file_field.name)[1].lower()
            file_field.name = f"{model_name}_{uuid.uuid4().hex}{extension}"
        super().save(*args, **kwargs)
