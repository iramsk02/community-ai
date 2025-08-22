# JSON Translator

**A small CLI utility to translate JSON string leaves into another language using LLM API**

## Index

1. [Overview](#overview)
2. [Key features](#key-features)
3. [Quick start](#quick-start)

   * [Prerequisites](#prerequisites)
   * [Install](#install)
   * [Configuration](#configuration)
   * [Run the translator (example)](#run-the-translator-example)
4. [File/Module walkthrough (what the code does)](#filemodule-walkthrough-what-the-code-does)

   * [prettify\_key(key)](#prettify_keykey)
   * [is\_suspicious(s: str) -> bool](#is_suspiciouss-str---bool)
   * [JSONTranslator class](#jsontranslator-class)
   * [CLI usage at the bottom of the file](#cli-usage-at-the-bottom-of-the-file)
5. [How the caching works](#how-the-caching-works)
6. [Adding support for a new language](#adding-support-for-a-new-language)
7. [Known issues & suggested fixes](#known-issues--suggested-fixes)
8. [Troubleshooting](#troubleshooting)
9. [Contribution](#contribution)
10. [Example `.env example`](#example-env-example)

**A small CLI utility to translate JSON string leaves into another language using the Groq LLM API**

---

## Overview

This repository contains a Python script that scans a JSON file for all string values (leaf nodes), sends those strings to a Groq LLM for translation, and writes a translated JSON file. It includes a simple persistent cache so repeated runs do not re-translate strings already translated previously.

The translator is implemented in `JSONTranslator` and uses the `groq` Python client, `python-dotenv` for configuration, `backoff` for retrying transient API errors, and `tqdm` for progress reporting.

---

## Key features

* Walk a JSON object and extract every string leaf for translation.
* Reconstruct the original JSON structure with translated string values.
* Persistent JSON translation cache per-target-language to avoid re-translating the same strings.
* Simple suspicious-translation detection to retry obviously invalid outputs (very short, punctuation-only, empty, or missing).
* Exponential backoff for API calls.

---

## Quick start

### Prerequisites

* Python 3.10+ (3.8+ may work but 3.10+ recommended)
* A Groq API key with access to the configured model

### Install

```bash
python -m venv .venv
source .venv/bin/activate      # on macOS / Linux
.\.venv\Scripts\activate     # on Windows (PowerShell)

pip install -r requirements.txt
```

`requirements.txt` (recommended contents):

```
groq
python-dotenv
backoff
tqdm
```

> If you prefer, you can simply `pip install groq python-dotenv backoff tqdm`.

### Configuration

Create a `.env` file in the project root with the following values:

```
GROQ_API_KEY="gsk_xxx..."
DEFAULT_TARGET_LANGUAGE="Latvian"
```

* `GROQ_API_KEY` — **required**. Your Groq API key.
* `DEFAULT_TARGET_LANGUAGE` — optional. The default target language used by the translator when not overridden. Example: `Portuguese`, `French`, `Hindi`, `Latvian`.

### Run the translator (example)

```bash
python translator.py
```

By default the script will attempt to translate the input file `en-US.json` and produce an output file named `test_translated_<language>.json` (for example `test_translated_Latvian.json`).

You can change the `INPUT_FILE` constant at the bottom of `translator.py` or modify the script to accept CLI arguments (recommended enhancement).

---

## File/Module walkthrough (what the code does)

### `prettify_key(key)`

Converts snake\_case or `mixedCase` JSON keys into a more human readable label. Example: `userName` → `User Name`, `error_message` → `Error Message`.

### `is_suspicious(s: str) -> bool`

Quick heuristics to decide whether a returned translation is likely invalid:

* `None` or empty after stripping
* Very short strings (≤ 2 chars)
* Strings composed only of punctuation characters

If suspicious, the script will retry translation up to a few times.

### `JSONTranslator` class

* `__init__(self, cache_file=None)`: loads environment variables using `python-dotenv`, reads `GROQ_API_KEY` and `DEFAULT_TARGET_LANGUAGE` and constructs a `Groq` client. Sets the default model name to `llama3-70b-8192` (changeable in the code).

* `load_translation_cache` / `save_translation_cache`: read/write a JSON file used as cache. The default cache filename is `translation_cache_<language>.json` (language derived from `DEFAULT_TARGET_LANGUAGE`) unless you pass `cache_file` explicitly.

* `_api_translate(self, prompt)`: a thin wrapper that calls `self.client.chat.completions.create(...)` and returns the model response text. This method is wrapped with `backoff.on_exception` to retry on exceptions.

* `translate_text(self, text, context="")`: builds a deterministic cache key (`text` + `_` + `context`). If cached, returns the cached translation. Otherwise, it constructs a clear prompt describing the target language and optional JSON path context and calls the Groq API. The function implements up to 5 attempts to avoid suspicious results. On complete failure, it falls back to returning the original English text.

* `all_strings(self, obj, path="")`: recursively yields all string leaf values along with the `context` (derived from the JSON path) and the path string used later for reconstruction.

* `apply_translated_strings(self, obj, translations_by_path, path="")`: rebuilds a JSON structure substituting strings according to the `translations_by_path` map.

* `get_context_from_path(self, path)`: attempts to convert the internal path representation into a human-friendly context string by splitting path components and prettifying them. (Note: the current implementation uses `re.split(r'\.|$$|$$', path)` which contains a likely bug — see "Known issues & suggested fixes" below.)

* `translate_json_file(self, input_file, output_file)`: orchestrates reading the input JSON, enumerating strings, translating what’s not in cache, reconstructing translated JSON, and writing the output file.

### CLI usage at the bottom of the file

A small example shows how to instantiate `JSONTranslator`, compute an output filename using the chosen language, and run `translate_json_file`.

---

## How the caching works

* The cache is a native JSON file stored on disk (default name: `translation_cache_<language>.json`).
* The code uses a cache key `${text}_${context}` where `context` is the human-friendly path derived by `get_context_from_path`.
* This means identical English texts occurring in different JSON locations will be cached separately if `context` differs.
* On each successful translation, the cache file is saved to disk.

**How to clear the cache**: delete the file `translation_cache_<language>.json` or pass a different `cache_file` when creating `JSONTranslator`.

---

## Adding support for a new language

There are two simple approaches:

1. **Change the `.env` value**

   * Update `.env` and set `DEFAULT_TARGET_LANGUAGE` to the desired language (for example `Portuguese`).
   * Run the script normally — it will create a language-specific cache file (e.g. `translation_cache_Portuguese.json`).

2. **Make target language configurable at runtime (recommended)**

   * Modify `JSONTranslator.__init__` to accept `target_language` as a constructor argument and use it instead of reading only from `.env`. For example:

     ```python
     def __init__(self, cache_file=None, target_language=None):
         load_dotenv()
         self.target_language = target_language or os.getenv("DEFAULT_TARGET_LANGUAGE", "Latvian")
     ```
   * This allows you to call `JSONTranslator(target_language="Hindi")` from another script or from the CLI.

**Important localization notes when adding languages**:

* Watch for placeholders and variables in strings such as `{count}`, `%s`, `{name}`. Update the prompt to instruct the model to keep placeholders unchanged and in-place.
* Grammar/pluralization: different languages handle plural forms differently. This script translates strings individually and does not implement ICU/plural rules. If you rely on pluralization tokens, prefer to keep pluralization keys separate and handle them with a localization framework.

---

## Known issues & suggested fixes

1. **`get_context_from_path` regex bug**

   * Current code: `raw_keys = re.split(r'\.|$$|$$', path)` — this pattern is incorrect and does not do what is intended.
   * Suggested fix: split on `.` or array indices with a safer approach. Example:

     ```python
     raw_keys = re.split(r'\.|\[|\]', path)
     raw_keys = [k for k in raw_keys if k]
     ```
   * This will yield components like `root`, `items`, `0`, `label` from `root.items[0].label`.

2. **Cache key collisions**

   * Using `text + '_' + context` can lead to collisions when `text` contains underscores or `context` is missing. A safer approach is to use a JSON-encoded tuple or an SHA256 digest:

     ```python
     import hashlib, json
     key = hashlib.sha256(json.dumps([text, context], ensure_ascii=False).encode('utf-8')).hexdigest()
     ```

3. **Placeholders in strings**

   * The prompt should explicitly tell the model to preserve placeholder tokens or markup.

4. **Large files & rate limits**

   * If you translate thousands of strings, consider chunking, adding a short delay between API calls, batching similar strings, or acquiring higher-rate quota from your provider.

5. **Model selection**

   * The code hard-codes a large model name: `llama3-70b-8192`. For speed or cost, allow configuring this via `.env` or an argument.

6. **Error handling and observability**

   * Consider switching `print()` debugging to Python `logging` with configurable log levels. This improves behavior in production and CI.

---

## Prompt design recommendations

To encourage safe, consistent translations:

* Provide context: include the JSON path or screen label.
* Instruct the model to **only return the translated text** (code already requests that).
* Tell the model to **preserve placeholders** such as `{name}`, `%s`, or HTML tags.
* Optionally add a small instruction to avoid transliteration of proper nouns.

Example improved prompt:

```
Translate the following English text into {target_language}. Keep placeholders (like {count}, {name}, %s) intact. Do not add any explanation — only return the translation.
Context: {context}
English: {text}
{target_language}:
```

---

## Tests and validation

* Unit tests are recommended for:

  * `all_strings` behavior (nested dicts, lists and mixed structures)
  * `apply_translated_strings` to ensure structural identity
  * `is_suspicious` heuristics
  * Cache read/write behavior
* Add CI (GitHub Actions) to run tests on push.

---

## Security & privacy

* Do not commit `.env` or any API keys to version control. Add `.env` to `.gitignore`.
* The script sends literal strings to a third-party API (Groq). Do not send sensitive PII or secrets.

---

## Troubleshooting

* **`Missing GROQ_API_KEY`**: ensure `.env` contains `GROQ_API_KEY` and you call `load_dotenv()` before reading.
* **Very short or empty translations**: the script retries up to 5 times; if still failing, check the prompt, model availability, or rate limits.
* **Large memory usage**: if input JSON is huge, consider streaming processing instead of building `all_strs` in memory.

---

## Recommended enhancements (future work)

* Add a proper CLI with `argparse` allowing input/output files, target language, model name, and cache file path.
* Add batching or parallel requests with careful rate-limit handling.
* Support placeholders and ICU message format detection/preservation.
* Integrate with i18n frameworks (Android, iOS, web frameworks) to output language-specific resource formats.
* Add a `--dry-run` mode that prints what would be translated without calling the API.

---

## Contribution

If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Open a pull request describing changes

Please include tests for new functionality.

---

## License

Add an appropriate license file (MIT, Apache-2.0, etc.) depending on how you want to share the code.

---

## Example `.env.example`

```
GROQ_API_KEY=your_groq_api_key_here
DEFAULT_TARGET_LANGUAGE=Portuguese
```

---

If you'd like, I can:

* generate a `requirements.txt`,
* convert the bottom-of-file usage into a proper CLI with `argparse`,
* create unit tests for the critical helpers (`all_strings`, `apply_translated_strings`, `is_suspicious`), or
* produce a GitHub Actions YAML to run tests automatically.

Tell me which of these you'd like next and I'll add it.
