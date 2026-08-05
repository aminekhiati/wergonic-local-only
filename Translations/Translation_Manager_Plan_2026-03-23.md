# Translation Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a translation management page in wergonic-admin that lets devs upload `en.json`, auto-translate missing keys to de/es/sv/nl using a free API, and download the translated files.

**Architecture:** Django backend handles JSON parsing, diffing, storage, and translation via `deep-translator` (free Google Translate wrapper). React frontend provides a clean upload/translate/download UI in wergonic-admin. Translations persist in a single Django model keyed by namespace + dotted key path.

**Tech Stack:** Django 5.1 + DRF, deep-translator (Python), React 18 + MUI 5 + React Query, i18next

---

## File Structure

### Django Backend (wergonic-django-backend)

| Action | File | Responsibility |
|--------|------|---------------|
| Create | `translations/__init__.py` | App init |
| Create | `translations/models.py` | TranslationEntry model |
| Create | `translations/serializers.py` | DRF serializers for CRUD + import/export |
| Create | `translations/views.py` | API views: import, export, translate, list |
| Create | `translations/urls.py` | URL routing |
| Create | `translations/utils.py` | JSON flatten/unflatten, translation API calls |
| Create | `translations/management/__init__.py` | Management command init |
| Create | `translations/management/commands/__init__.py` | Management command init |
| Create | `translations/management/commands/seed_translations.py` | Seed DB from existing JSON files |
| Modify | `core/settings.py:74` | Add `translations` to INSTALLED_APPS |
| Modify | `core/urls.py:32` | Add translations URL include |
| Modify | `requirements.txt` | Add `deep-translator` |

### React Frontend (wergonic-web-apps/apps/wergonic-admin)

| Action | File | Responsibility |
|--------|------|---------------|
| Create | `src/pages/TranslationsPage/TranslationsPage.tsx` | Page component |
| Create | `src/pages/TranslationsPage/index.ts` | Default export |
| Create | `src/features/translations/index.ts` | Feature barrel export |
| Create | `src/features/translations/components/TranslationManager/TranslationManager.tsx` | Main UI: upload, translate, download |
| Create | `src/features/translations/components/TranslationManager/TranslationManager.hooks.ts` | API calls, state management |
| Create | `src/features/translations/components/TranslationManager/index.ts` | Component export |
| Create | `src/api/translations.ts` | API functions |
| Create | `src/types/translations.ts` | TypeScript types |
| Modify | `src/api/apiRoutes.ts:90` | Add translations routes |
| Modify | `src/api/index.ts:14` | Export translation API functions |
| Modify | `src/routes/routes.ts:38` | Add translations route |
| Modify | `src/routes/AppRoutes.tsx:18,38` | Lazy load + route for TranslationsPage |
| Modify | `src/features/dashboard/components/MainLayout/DrawerMenu/DrawerMenu.hooks.ts:33` | Add sidebar item |

---

## Task 1: Django — Translation Model + Migration

**Files:**
- Create: `translations/__init__.py`
- Create: `translations/models.py`
- Modify: `core/settings.py:74`

- [ ] **Step 1: Create the translations app directory**

```bash
cd D:/Projects/Wergonic/wergonic-django-backend
mkdir translations
```

- [ ] **Step 2: Create `translations/__init__.py`**

Empty file.

- [ ] **Step 3: Create `translations/models.py`**

```python
from django.db import models


class TranslationEntry(models.Model):
    NAMESPACE_CHOICES = [
        ("web-ui", "Web UI (shared)"),
        ("client-panel", "Client Panel"),
        ("flutter", "Flutter App"),
    ]

    namespace = models.CharField(max_length=50, choices=NAMESPACE_CHOICES)
    key = models.CharField(max_length=500)
    en = models.TextField(default="")
    de = models.TextField(blank=True, default="")
    es = models.TextField(blank=True, default="")
    sv = models.TextField(blank=True, default="")
    nl = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("namespace", "key")
        ordering = ["namespace", "key"]

    def __str__(self):
        return f"[{self.namespace}] {self.key}"
```

- [ ] **Step 4: Add to INSTALLED_APPS in `core/settings.py`**

After line 75 (`"workcycles"`), add `"translations"`.

- [ ] **Step 5: Run migration**

```bash
python manage.py makemigrations translations
python manage.py migrate
```

---

## Task 2: Django — Utility Functions (flatten/unflatten JSON + translate)

**Files:**
- Create: `translations/utils.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Add `deep-translator` to requirements.txt**

Append `deep-translator==1.11.4` to `requirements.txt`.

- [ ] **Step 2: Install the package**

```bash
pip install deep-translator==1.11.4
```

- [ ] **Step 3: Create `translations/utils.py`**

```python
import json
import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "de": "de",
    "es": "es",
    "sv": "sv",
    "nl": "nl",
}


def flatten_json(nested_json, prefix=""):
    """Flatten nested JSON to dot-notation keys.

    Example: {"a": {"b": "c"}} -> {"a.b": "c"}
    """
    items = {}
    for key, value in nested_json.items():
        new_key = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key))
        else:
            items[new_key] = value
    return items


def unflatten_json(flat_json):
    """Unflatten dot-notation keys back to nested JSON.

    Example: {"a.b": "c"} -> {"a": {"b": "c"}}
    """
    result = {}
    for key, value in flat_json.items():
        parts = key.split(".")
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


def translate_text(text, target_lang):
    """Translate a single text string using Google Translate (free)."""
    if not text or not text.strip():
        return text
    try:
        translated = GoogleTranslator(source="en", target=target_lang).translate(text)
        return translated or text
    except Exception as e:
        logger.warning(f"Translation failed for '{text[:50]}...' to {target_lang}: {e}")
        return ""


def translate_batch(texts, target_lang, batch_size=50):
    """Translate a list of texts in batches. Returns list of translated texts."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for text in batch:
            results.append(translate_text(text, target_lang))
    return results
```

---

## Task 3: Django — Serializers

**Files:**
- Create: `translations/serializers.py`

- [ ] **Step 1: Create `translations/serializers.py`**

```python
from rest_framework import serializers
from .models import TranslationEntry


class TranslationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationEntry
        fields = ("id", "namespace", "key", "en", "de", "es", "sv", "nl", "updated_at")
        read_only_fields = ("id", "updated_at")


class ImportRequestSerializer(serializers.Serializer):
    namespace = serializers.ChoiceField(choices=TranslationEntry.NAMESPACE_CHOICES)
    file = serializers.FileField()


class ExportRequestSerializer(serializers.Serializer):
    namespace = serializers.ChoiceField(choices=TranslationEntry.NAMESPACE_CHOICES)
    language = serializers.ChoiceField(choices=[
        ("de", "German"),
        ("es", "Spanish"),
        ("sv", "Swedish"),
        ("nl", "Dutch"),
    ])


class TranslateRequestSerializer(serializers.Serializer):
    namespace = serializers.ChoiceField(choices=TranslationEntry.NAMESPACE_CHOICES)
    languages = serializers.MultipleChoiceField(
        choices=[("de", "German"), ("es", "Spanish"), ("sv", "Swedish"), ("nl", "Dutch")],
        required=False,
    )
```

---

## Task 4: Django — API Views

**Files:**
- Create: `translations/views.py`

- [ ] **Step 1: Create `translations/views.py`**

```python
import json
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import TranslationEntry
from .serializers import (
    TranslationEntrySerializer,
    ImportRequestSerializer,
    ExportRequestSerializer,
    TranslateRequestSerializer,
)
from .utils import flatten_json, unflatten_json, translate_text, SUPPORTED_LANGUAGES
from core.search_filter import StartsWithSearchFilter


class TranslationListView(generics.ListAPIView):
    """List all translations, filterable by namespace."""
    serializer_class = TranslationEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, StartsWithSearchFilter, filters.OrderingFilter]
    search_fields = ["key", "en"]
    ordering_fields = "__all__"
    filterset_fields = ["namespace"]

    def get_queryset(self):
        return TranslationEntry.objects.all()


class TranslationImportView(APIView):
    """Import en.json file. Creates new keys, updates changed English values."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ImportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        namespace = serializer.validated_data["namespace"]
        file = serializer.validated_data["file"]

        try:
            content = json.loads(file.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {"error": "Invalid JSON file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        flat = flatten_json(content)

        new_count = 0
        updated_count = 0
        unchanged_count = 0

        for key, value in flat.items():
            if not isinstance(value, str):
                value = str(value)

            entry, created = TranslationEntry.objects.get_or_create(
                namespace=namespace,
                key=key,
                defaults={"en": value},
            )

            if created:
                new_count += 1
            elif entry.en != value:
                entry.en = value
                # Clear translations when English text changes
                entry.de = ""
                entry.es = ""
                entry.sv = ""
                entry.nl = ""
                entry.save()
                updated_count += 1
            else:
                unchanged_count += 1

        return Response({
            "new_keys": new_count,
            "updated_keys": updated_count,
            "unchanged_keys": unchanged_count,
            "total_keys": len(flat),
        })


class TranslationExportView(APIView):
    """Export translations as nested JSON for a given namespace + language."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        namespace = request.query_params.get("namespace")
        language = request.query_params.get("language")

        if not namespace or not language:
            return Response(
                {"error": "namespace and language are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if language not in SUPPORTED_LANGUAGES and language != "en":
            return Response(
                {"error": f"Unsupported language: {language}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entries = TranslationEntry.objects.filter(namespace=namespace)
        flat = {}
        for entry in entries:
            value = getattr(entry, language, "")
            flat[entry.key] = value if value else ""

        nested = unflatten_json(flat)

        return Response(nested)


class TranslationTranslateView(APIView):
    """Auto-translate missing keys for selected languages."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = TranslateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        namespace = serializer.validated_data["namespace"]
        languages = serializer.validated_data.get("languages", list(SUPPORTED_LANGUAGES.keys()))

        entries = TranslationEntry.objects.filter(namespace=namespace)
        translated_count = {lang: 0 for lang in languages}

        for entry in entries:
            if not entry.en:
                continue
            for lang in languages:
                current_value = getattr(entry, lang, "")
                if not current_value:
                    translated = translate_text(entry.en, SUPPORTED_LANGUAGES[lang])
                    if translated:
                        setattr(entry, lang, translated)
                        translated_count[lang] += 1
            entry.save()

        return Response({
            "translated_counts": translated_count,
            "total_entries": entries.count(),
        })


class TranslationStatsView(APIView):
    """Get translation stats per namespace."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        namespace = request.query_params.get("namespace")
        if not namespace:
            return Response(
                {"error": "namespace is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entries = TranslationEntry.objects.filter(namespace=namespace)
        total = entries.count()

        stats = {"total_keys": total}
        for lang in SUPPORTED_LANGUAGES:
            filled = entries.exclude(**{lang: ""}).count()
            stats[f"{lang}_translated"] = filled
            stats[f"{lang}_missing"] = total - filled

        return Response(stats)
```

---

## Task 5: Django — URLs + Wire Up

**Files:**
- Create: `translations/urls.py`
- Modify: `core/urls.py:32`

- [ ] **Step 1: Create `translations/urls.py`**

```python
from django.urls import path
from . import views

app_name = "translations"

urlpatterns = [
    path("", views.TranslationListView.as_view(), name="list"),
    path("import/", views.TranslationImportView.as_view(), name="import"),
    path("export/", views.TranslationExportView.as_view(), name="export"),
    path("translate/", views.TranslationTranslateView.as_view(), name="translate"),
    path("stats/", views.TranslationStatsView.as_view(), name="stats"),
]
```

- [ ] **Step 2: Add to `core/urls.py`**

Add after line 32 (notifications):
```python
path("translations/", include("translations.urls", namespace="Translations")),
```

---

## Task 6: Django — Seed Management Command

**Files:**
- Create: `translations/management/__init__.py`
- Create: `translations/management/commands/__init__.py`
- Create: `translations/management/commands/seed_translations.py`

- [ ] **Step 1: Create directory structure and `__init__.py` files**

```bash
mkdir -p translations/management/commands
touch translations/management/__init__.py
touch translations/management/commands/__init__.py
```

- [ ] **Step 2: Create `seed_translations.py`**

This command reads the JSON files from the other repos (pass paths as arguments) and seeds the DB.

```python
import json
from django.core.management.base import BaseCommand
from translations.models import TranslationEntry
from translations.utils import flatten_json


SEED_CONFIG = [
    {
        "namespace": "web-ui",
        "description": "Web UI shared translations",
    },
    {
        "namespace": "client-panel",
        "description": "Client Panel translations",
    },
    {
        "namespace": "flutter",
        "description": "Flutter app translations",
    },
]

LANGUAGES = ["en", "de", "es", "sv", "nl"]


class Command(BaseCommand):
    help = "Seed translation entries from JSON files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            type=str,
            required=True,
            help="Directory containing language JSON files (en.json, de.json, etc.)",
        )
        parser.add_argument(
            "--namespace",
            type=str,
            required=True,
            choices=[c["namespace"] for c in SEED_CONFIG],
            help="Namespace for these translations",
        )
        parser.add_argument(
            "--nl-filename",
            type=str,
            default="nl.json",
            help="Filename for Dutch translations (default: nl.json, use nl-NL.json for web)",
        )

    def handle(self, *args, **options):
        directory = options["dir"]
        namespace = options["namespace"]
        nl_filename = options["nl_filename"]

        # Load all language files
        lang_data = {}
        filenames = {
            "en": "en.json",
            "de": "de.json",
            "es": "es.json",
            "sv": "sv.json",
            "nl": nl_filename,
        }

        for lang, filename in filenames.items():
            filepath = f"{directory}/{filename}"
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    lang_data[lang] = flatten_json(content)
                    self.stdout.write(f"Loaded {filepath}: {len(lang_data[lang])} keys")
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"File not found: {filepath}, skipping"))
                lang_data[lang] = {}

        if "en" not in lang_data or not lang_data["en"]:
            self.stderr.write(self.style.ERROR("English file is required"))
            return

        # Create or update entries
        created = 0
        updated = 0
        for key, en_value in lang_data["en"].items():
            if not isinstance(en_value, str):
                en_value = str(en_value)

            defaults = {"en": en_value}
            for lang in ["de", "es", "sv", "nl"]:
                value = lang_data.get(lang, {}).get(key, "")
                if not isinstance(value, str):
                    value = str(value) if value else ""
                defaults[lang] = value

            _, was_created = TranslationEntry.objects.update_or_create(
                namespace=namespace,
                key=key,
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"[{namespace}] Done: {created} created, {updated} updated"
            )
        )
```

- [ ] **Step 3: Run the seed command for all three namespaces**

```bash
cd D:/Projects/Wergonic/wergonic-django-backend

# Web UI shared translations
python manage.py seed_translations \
  --dir "../wergonic-web-apps/packages/ui/src/assets/locals" \
  --namespace "web-ui" \
  --nl-filename "nl-NL.json"

# Client Panel translations
python manage.py seed_translations \
  --dir "../wergonic-web-apps/apps/client-panel/src/assets/locals" \
  --namespace "client-panel" \
  --nl-filename "nl-NL.json"

# Flutter translations
python manage.py seed_translations \
  --dir "../wergonic-flutter/assets/translations" \
  --namespace "flutter" \
  --nl-filename "nl.json"
```

Note: The seed command only needs to run once locally. On the production server, run `python manage.py migrate` first, then the seed command with the JSON files copied over (or committed as fixtures).

---

## Task 7: React — Types + API Layer

**Files:**
- Create: `src/types/translations.ts`
- Create: `src/api/translations.ts`
- Modify: `src/api/apiRoutes.ts`
- Modify: `src/api/index.ts`

- [ ] **Step 1: Create `src/types/translations.ts`**

```typescript
export type TTranslationStats = {
    total_keys: number;
    de_translated: number;
    de_missing: number;
    es_translated: number;
    es_missing: number;
    sv_translated: number;
    sv_missing: number;
    nl_translated: number;
    nl_missing: number;
};

export type TImportResult = {
    new_keys: number;
    updated_keys: number;
    unchanged_keys: number;
    total_keys: number;
};

export type TTranslateResult = {
    translated_counts: Record<string, number>;
    total_entries: number;
};

export type TNamespace = "web-ui" | "client-panel" | "flutter";

export type TLanguage = "de" | "es" | "sv" | "nl";
```

- [ ] **Step 2: Add to `src/api/apiRoutes.ts`**

Add before the closing `};`:

```typescript
translations: {
    stats: (namespace: string) => `/translations/stats/?namespace=${namespace}`,
    import: `/translations/import/`,
    export: (namespace: string, language: string) =>
        `/translations/export/?namespace=${namespace}&language=${language}`,
    translate: `/translations/translate/`,
},
```

- [ ] **Step 3: Create `src/api/translations.ts`**

```typescript
import { api } from "@services/index";
import { apiRoutes } from "./apiRoutes";
import { TTranslationStats, TImportResult, TTranslateResult } from "@appTypes/translations";

export const getTranslationStats = (namespace: string) =>
    api.get<TTranslationStats>(apiRoutes.translations.stats(namespace));

export const importTranslations = (namespace: string, file: File) => {
    const formData = new FormData();
    formData.append("namespace", namespace);
    formData.append("file", file);
    return api.post<TImportResult>(apiRoutes.translations.import, formData);
};

export const exportTranslations = (namespace: string, language: string) =>
    api.get<Record<string, unknown>>(apiRoutes.translations.export(namespace, language));

export const translateMissing = (namespace: string, languages?: string[]) =>
    api.post<TTranslateResult>(apiRoutes.translations.translate, {
        namespace,
        languages,
    });
```

- [ ] **Step 4: Add exports to `src/api/index.ts`**

Append:
```typescript
export { getTranslationStats, importTranslations, exportTranslations, translateMissing } from "./translations";
```

---

## Task 8: React — Translation Manager Component

**Files:**
- Create: `src/features/translations/components/TranslationManager/TranslationManager.hooks.ts`
- Create: `src/features/translations/components/TranslationManager/TranslationManager.tsx`
- Create: `src/features/translations/components/TranslationManager/index.ts`
- Create: `src/features/translations/index.ts`

- [ ] **Step 1: Create `TranslationManager.hooks.ts`**

```typescript
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useSnackbar } from "notistack";
import { getTranslationStats, importTranslations, exportTranslations, translateMissing } from "@api/index";
import { TNamespace, TLanguage } from "@appTypes/translations";

const NAMESPACES: { value: TNamespace; label: string }[] = [
    { value: "web-ui", label: "Web UI (shared)" },
    { value: "client-panel", label: "Client Panel" },
    { value: "flutter", label: "Flutter App" },
];

const LANGUAGES: { value: TLanguage; label: string }[] = [
    { value: "de", label: "German (DE)" },
    { value: "es", label: "Spanish (ES)" },
    { value: "sv", label: "Swedish (SV)" },
    { value: "nl", label: "Dutch (NL)" },
];

export const useTranslationManager = () => {
    const { enqueueSnackbar } = useSnackbar();
    const [selectedNamespace, setSelectedNamespace] = useState<TNamespace>("web-ui");
    const [selectedLanguages, setSelectedLanguages] = useState<TLanguage[]>(["de", "es", "sv", "nl"]);

    const statsQuery = useQuery({
        queryKey: ["translationStats", selectedNamespace],
        queryFn: () => getTranslationStats(selectedNamespace).then((res) => res.data),
    });

    const importMutation = useMutation({
        mutationFn: (file: File) => importTranslations(selectedNamespace, file),
        onSuccess: (res) => {
            const { new_keys, updated_keys } = res.data;
            enqueueSnackbar(
                `Import complete: ${new_keys} new keys, ${updated_keys} updated keys`,
                { variant: "success" }
            );
            statsQuery.refetch();
        },
        onError: () => {
            enqueueSnackbar("Failed to import file", { variant: "error" });
        },
    });

    const translateMutation = useMutation({
        mutationFn: () => translateMissing(selectedNamespace, selectedLanguages),
        onSuccess: (res) => {
            const counts = res.data.translated_counts;
            const summary = Object.entries(counts)
                .map(([lang, count]) => `${lang}: ${count}`)
                .join(", ");
            enqueueSnackbar(`Translation complete: ${summary}`, { variant: "success" });
            statsQuery.refetch();
        },
        onError: () => {
            enqueueSnackbar("Translation failed", { variant: "error" });
        },
    });

    const handleExport = async (language: TLanguage) => {
        try {
            const res = await exportTranslations(selectedNamespace, language);
            const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");

            // Use nl-NL.json for web namespaces, nl.json for flutter
            let filename = `${language}.json`;
            if (language === "nl" && selectedNamespace !== "flutter") {
                filename = "nl-NL.json";
            }

            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        } catch {
            enqueueSnackbar(`Failed to export ${language}`, { variant: "error" });
        }
    };

    const handleExportAll = async () => {
        for (const lang of selectedLanguages) {
            await handleExport(lang);
        }
    };

    return {
        NAMESPACES,
        LANGUAGES,
        selectedNamespace,
        setSelectedNamespace,
        selectedLanguages,
        setSelectedLanguages,
        stats: statsQuery.data,
        isLoadingStats: statsQuery.isLoading,
        importMutation,
        translateMutation,
        handleExport,
        handleExportAll,
    };
};
```

- [ ] **Step 2: Create `TranslationManager.tsx`**

```tsx
import { useRef } from "react";
import {
    Box,
    Button,
    Card,
    CardContent,
    Checkbox,
    Chip,
    CircularProgress,
    FormControlLabel,
    FormGroup,
    LinearProgress,
    MenuItem,
    Select,
    Stack,
    Typography,
} from "@mui/material";
import {
    CloudUpload as UploadIcon,
    Translate as TranslateIcon,
    Download as DownloadIcon,
} from "@mui/icons-material";
import { useTranslationManager } from "./TranslationManager.hooks";
import { TLanguage } from "@appTypes/translations";

export const TranslationManager = () => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const {
        NAMESPACES,
        LANGUAGES,
        selectedNamespace,
        setSelectedNamespace,
        selectedLanguages,
        setSelectedLanguages,
        stats,
        isLoadingStats,
        importMutation,
        translateMutation,
        handleExport,
        handleExportAll,
    } = useTranslationManager();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            importMutation.mutate(file);
            e.target.value = "";
        }
    };

    const toggleLanguage = (lang: TLanguage) => {
        setSelectedLanguages((prev) =>
            prev.includes(lang) ? prev.filter((l) => l !== lang) : [...prev, lang]
        );
    };

    const totalMissing = stats
        ? (stats.de_missing || 0) + (stats.es_missing || 0) + (stats.sv_missing || 0) + (stats.nl_missing || 0)
        : 0;

    return (
        <Stack spacing={3}>
            {/* Namespace Selector */}
            <Card>
                <CardContent>
                    <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                        Namespace
                    </Typography>
                    <Select
                        value={selectedNamespace}
                        onChange={(e) => setSelectedNamespace(e.target.value as typeof selectedNamespace)}
                        size="small"
                        fullWidth
                    >
                        {NAMESPACES.map((ns) => (
                            <MenuItem key={ns.value} value={ns.value}>
                                {ns.label}
                            </MenuItem>
                        ))}
                    </Select>
                </CardContent>
            </Card>

            {/* Stats */}
            <Card>
                <CardContent>
                    <Typography variant="subtitle2" sx={{ mb: 2 }}>
                        Translation Status
                    </Typography>
                    {isLoadingStats ? (
                        <CircularProgress size={24} />
                    ) : stats ? (
                        <Stack spacing={1.5}>
                            <Typography variant="body2" color="text.secondary">
                                Total keys: <strong>{stats.total_keys}</strong>
                            </Typography>
                            {LANGUAGES.map((lang) => {
                                const translated = stats[`${lang.value}_translated` as keyof typeof stats] as number;
                                const total = stats.total_keys;
                                const pct = total > 0 ? Math.round((translated / total) * 100) : 0;
                                return (
                                    <Box key={lang.value}>
                                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                                            <Typography variant="body2">{lang.label}</Typography>
                                            <Chip
                                                label={`${translated}/${total} (${pct}%)`}
                                                size="small"
                                                color={pct === 100 ? "success" : pct > 50 ? "warning" : "error"}
                                            />
                                        </Stack>
                                        <LinearProgress
                                            variant="determinate"
                                            value={pct}
                                            sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
                                        />
                                    </Box>
                                );
                            })}
                        </Stack>
                    ) : (
                        <Typography variant="body2" color="text.secondary">
                            No data yet. Import an English file to get started.
                        </Typography>
                    )}
                </CardContent>
            </Card>

            {/* Import */}
            <Card>
                <CardContent>
                    <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                        Import English File
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Upload your en.json file. New keys will be added, changed keys will be flagged for re-translation.
                    </Typography>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".json"
                        onChange={handleFileChange}
                        style={{ display: "none" }}
                    />
                    <Button
                        variant="contained"
                        startIcon={importMutation.isLoading ? <CircularProgress size={18} /> : <UploadIcon />}
                        onClick={() => fileInputRef.current?.click()}
                        disabled={importMutation.isLoading}
                    >
                        {importMutation.isLoading ? "Importing..." : "Upload en.json"}
                    </Button>
                    {importMutation.data && (
                        <Box sx={{ mt: 2 }}>
                            <Chip
                                label={`${importMutation.data.data.new_keys} new`}
                                color="success"
                                size="small"
                                sx={{ mr: 1 }}
                            />
                            <Chip
                                label={`${importMutation.data.data.updated_keys} updated`}
                                color="warning"
                                size="small"
                                sx={{ mr: 1 }}
                            />
                            <Chip
                                label={`${importMutation.data.data.unchanged_keys} unchanged`}
                                size="small"
                            />
                        </Box>
                    )}
                </CardContent>
            </Card>

            {/* Translate */}
            <Card>
                <CardContent>
                    <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                        Auto-Translate Missing
                    </Typography>
                    <FormGroup row sx={{ mb: 2 }}>
                        {LANGUAGES.map((lang) => (
                            <FormControlLabel
                                key={lang.value}
                                control={
                                    <Checkbox
                                        checked={selectedLanguages.includes(lang.value)}
                                        onChange={() => toggleLanguage(lang.value)}
                                        size="small"
                                    />
                                }
                                label={lang.label}
                            />
                        ))}
                    </FormGroup>
                    <Button
                        variant="contained"
                        color="secondary"
                        startIcon={translateMutation.isLoading ? <CircularProgress size={18} /> : <TranslateIcon />}
                        onClick={() => translateMutation.mutate()}
                        disabled={translateMutation.isLoading || totalMissing === 0}
                    >
                        {translateMutation.isLoading
                            ? "Translating..."
                            : `Translate ${totalMissing} Missing Keys`}
                    </Button>
                    {translateMutation.data && (
                        <Box sx={{ mt: 2 }}>
                            {Object.entries(translateMutation.data.data.translated_counts).map(
                                ([lang, count]) => (
                                    <Chip
                                        key={lang}
                                        label={`${lang}: ${count} translated`}
                                        color="success"
                                        size="small"
                                        sx={{ mr: 1 }}
                                    />
                                )
                            )}
                        </Box>
                    )}
                </CardContent>
            </Card>

            {/* Export */}
            <Card>
                <CardContent>
                    <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
                        Export Translations
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                        {LANGUAGES.map((lang) => (
                            <Button
                                key={lang.value}
                                variant="outlined"
                                size="small"
                                startIcon={<DownloadIcon />}
                                onClick={() => handleExport(lang.value)}
                            >
                                {lang.label}
                            </Button>
                        ))}
                        <Button
                            variant="contained"
                            size="small"
                            startIcon={<DownloadIcon />}
                            onClick={handleExportAll}
                        >
                            Download All
                        </Button>
                    </Stack>
                </CardContent>
            </Card>
        </Stack>
    );
};
```

- [ ] **Step 3: Create barrel exports**

`src/features/translations/components/TranslationManager/index.ts`:
```typescript
export { TranslationManager } from "./TranslationManager";
```

`src/features/translations/index.ts`:
```typescript
export { TranslationManager } from "./components/TranslationManager";
```

---

## Task 9: React — Page + Route + Sidebar

**Files:**
- Create: `src/pages/TranslationsPage/TranslationsPage.tsx`
- Create: `src/pages/TranslationsPage/index.ts`
- Modify: `src/routes/routes.ts:38`
- Modify: `src/routes/AppRoutes.tsx`
- Modify: `src/features/dashboard/components/MainLayout/DrawerMenu/DrawerMenu.hooks.ts`

- [ ] **Step 1: Create `TranslationsPage.tsx`**

```tsx
import { DashboardInnerLayout } from "@features/dashboard";
import { TranslationManager } from "@features/translations";

export const TranslationsPage = () => {
    return (
        <DashboardInnerLayout header="Translations">
            <TranslationManager />
        </DashboardInnerLayout>
    );
};
```

- [ ] **Step 2: Create `src/pages/TranslationsPage/index.ts`**

```typescript
export { TranslationsPage as default } from "./TranslationsPage";
```

- [ ] **Step 3: Add route to `routes.ts`**

Add after `firmwares` block:
```typescript
translations: {
    index: ["translations"],
},
```

- [ ] **Step 4: Add lazy route to `AppRoutes.tsx`**

Add import:
```typescript
const TranslationsPage = lazy(() => import("@pages/TranslationsPage"));
```

Add Route inside `<MainLayout>` block:
```tsx
<Route path={r.gar(r.routes.translations.index)} element={<TranslationsPage />} />
```

- [ ] **Step 5: Add sidebar item to `DrawerMenu.hooks.ts`**

Add to `drawerMenuList` array (use TranslateIcon from MUI or use an existing icon with "fill" class):

```typescript
{
    text: "Translations",
    route: r.gar(r.routes.translations.index),
    icon: TranslateIcon,
    iconClassName: "fill",
},
```

Note: Need to import `TranslateIcon` from MUI icons — but the existing sidebar uses custom SVG icons from the `ui` package. Check if there's a `TranslateIcon` available, otherwise use a simple `Translate` from `@mui/icons-material`. The sidebar component may need to handle MUI icons differently from custom SVG icons — verify the icon rendering pattern.

---

## Task 10: Commit + Push

- [ ] **Step 1: Commit Django backend**

```bash
cd D:/Projects/Wergonic/wergonic-django-backend
git add translations/ core/settings.py core/urls.py requirements.txt
git commit --author="aminekhiati <amine.khiati14@gmail.com>" -m "feat: add translation manager API"
```

- [ ] **Step 2: Commit React frontend**

```bash
cd D:/Projects/Wergonic/wergonic-web-apps
git add apps/wergonic-admin/src/
git commit --author="aminekhiati <amine.khiati14@gmail.com>" -m "feat: add translation manager page in admin"
```

- [ ] **Step 3: Push both repos to main**

```bash
cd D:/Projects/Wergonic/wergonic-django-backend && git push origin main
cd D:/Projects/Wergonic/wergonic-web-apps && git push origin main
```
