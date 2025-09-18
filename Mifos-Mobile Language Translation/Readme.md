# Android Files Language Translator

Translate Android `strings.xml` resources from English into any target language using the Groq LLM API. The tool parses XML safely, aligns keys, retries on transient failures, caches results, and writes a clean, pretty-printed `strings.xml` for the target language.

---

## Table of Contents

- [Android XML Localization Translator (Groq)](#android-xml-localization-translator-groq)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Key Features](#key-features)
  - [How It Works](#how-it-works)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Project Layout Expectations](#project-layout-expectations)
  - [Basic Usage](#basic-usage)
  - [Adding a New Language](#adding-a-new-language)
  - [What Gets Translated](#what-gets-translated)
  - [Caching Behavior](#caching-behavior)
  - [Error Handling \& Retries](#error-handling--retries)
  - [Performance Tips](#performance-tips)
  - [Troubleshooting](#troubleshooting)
  - [Security Notes](#security-notes)
  - [Customization](#customization)
    - [Model](#model)
    - [Cache](#cache)
  - [Future Improvements](#future-improvements)

---

## Overview

This script localizes Android resource files by comparing the **English base** (`values/strings.xml`) with a **target language** file (e.g., `values-fr/strings.xml`) and producing a translated output in a sibling folder (e.g., `values-fr-auto/strings.xml`). It:

* Parses XML for `<string>` and `<string-array>` entries.
* Skips `translatable="false"` items.
* Calls the Groq Chat Completions API with a focused prompt.
* Retries on errors and filters obviously bad outputs.
* Caches translations to avoid rework.
* Pretty-prints the final XML.

## Key Features

* **Safe XML parsing** with `xml.etree.ElementTree` and clean pretty-printing via `minidom`.
* **Translation cache** per language on disk (JSON) to skip already translated segments.
* **Backoff & retry** for API reliability, plus a **suspicious-output** guard.
* **Repo-wide batching**: find all target `strings.xml` under a given `values-xx` folder and translate them in one pass.
* **Non-destructive output**: writes to `values-<lang>-auto/strings.xml` so your original files remain untouched.

## How It Works

1. **Discovery** (optional): `collect_translation_files(repo_root, source_folder)` walks the repository and collects all `strings.xml` files whose path contains `source_folder` (e.g., `values-fr`). For each, it pairs the base English file by swapping `source_folder` with `values`.
2. **Parsing**: `parse_xml_file` extracts all `<string>` and `<string-array>` entries, ignoring `translatable="false"`.
3. **Alignment**: `get_translatable_strings` matches entries by their `name` attribute. For arrays, items are aligned by index (up to the minimum length of both arrays).
4. **Translation**: For each unmatched cache entry, `translate_text` prompts the Groq model and retries if the response looks suspicious.
5. **Write-out**: Translated content is injected into a copy of the target XML tree and saved as a pretty-printed file in `values-xx-auto/strings.xml`.


## Requirements

* Python **3.9+**
* A Groq API key

Python packages:

```bash
pip install groq python-dotenv backoff tqdm
```

## Installation

```bash
# 1) Clone your repo (if not already cloned)
# git clone <your-repo-url>
# cd <your-repo>

# 2) Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
. .venv/Scripts/activate
# macOS/Linux
source .venv/bin/activate

# 3) Install dependencies
pip install groq python-dotenv backoff tqdm
```

## Configuration

Create a `.env` at the project root with:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
# Optional default if you import without passing target_language
DEFAULT_TARGET_LANGUAGE=Polish
```

**Model**: The script defaults to `openai/gpt-oss-120b`. You can change `self.model_name` inside `XMLTranslator.__init__`.

## Project Layout Expectations

The translator expects Android-style resource folders. Example:

```
app/
  src/main/res/
    values/strings.xml              # English base
    values-fr/strings.xml           # Target language source
    values-fr-auto/strings.xml      # Output (generated)
```

If your repo differs, adjust `repo_root` and `source_folder` accordingly.

## Basic Usage

Run the script directly (uses the `__main__` block):

```bash
python path/to/your_script.py
```

The default example in `__main__` is:

```python
if __name__ == "__main__":
    repo_root = "./app"
    translate_repo(
    repo_root="./app",          # or the root of your Android project
    source_folder="values-fr",  # the language folder to translate FROM (often values-xx)
    target_language="French",   # human-readable target language name
)
```

This will:

* Walk `./app` for any `strings.xml` under `values-ar`.
* Pair each with the corresponding `values/strings.xml`.
* Write translations to `values-ar-auto/strings.xml`.

## Adding a New Language

1. **Create the target folder**: copy the English file to a new language folder.

   ```
   app/src/main/res/values/strings.xml        # English base
   app/src/main/res/values-pl/strings.xml     # New language seed (copy of English)
   ```
2. **Run the translator** for that folder and language name:

   ```python
   translate_repo(
       repo_root="./app",
       source_folder="values-pl",
       target_language="Polish"
   )
   ```
3. **Review the output** in `values-pl-auto/strings.xml` and merge as needed.

> Why copy English first? The translator aligns by key names and array indices present in **both** files. Having a seed `values-xx/strings.xml` with the same keys ensures full coverage.

## What Gets Translated

* `<string name="…">…</string>` where `translatable` is not set to `false`.
* `<string-array name="…"> <item>…</item> … </string-array>` items, aligned by index up to the min length of both arrays.

**Skipped**

* Any entry with `translatable="false"`.
* Keys present in English but missing from the target file (create them first in the target file to translate).

## Caching Behavior

* Cache key: `"<english_text>_<context>"`.
* Cache file: `translation_cache_<target_language_lower>.json` by default (configurable).
* If a cache hit exists, the API is not called.
* Cache persists across runs. Delete or rename to force re-translation.

## Error Handling & Retries

* `_api_translate` is decorated with `backoff.on_exception(backoff.expo, Exception, max_tries=5)`.
* An additional **manual retry loop** (up to 5 attempts) triggers if output looks suspicious (empty, extremely short, or only punctuation).
* On persistent failure, the original English text is used as a fallback so the pipeline completes.

## Performance Tips

* Run with an initialized target file that mirrors English keys to minimize misses.
* Keep the cache file per language to avoid repeat calls across modules.
* Turn off verbose prints once validated (the code logs input/output for debugging).

## Troubleshooting

**Missing GROQ\_API\_KEY**

* Ensure `.env` exists at the project root and contains `GROQ_API_KEY`.

**Nothing is translated**

* Confirm your `source_folder` exists and contains `strings.xml`.
* Ensure English base file exists at the paired path (folder name `values`).
* Verify keys exist in both files.

**Some array items are untranslated**

* Only the first `min(len(english_items), len(target_items))` items are processed. Ensure arrays have matching lengths.



## Security Notes

* Do not commit `.env` or cache files containing sensitive data.
* Limit access to your Groq API key and rotate it periodically.

## Customization

### Model

Change the model in `XMLTranslator.__init__`:

```python
self.model_name = "openai/gpt-oss-120b"
```

### Cache

Set a custom cache path via `translate_repo(..., cache_file="path/to/cache.json")`.

## Future Improvements

* Make a standalone tool which can be used in future to translate only the newly added parts of the language.
* Periodically check with more improved LLM models coming out to enhance the translations

