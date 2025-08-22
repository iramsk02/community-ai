
import os
import json
import re
from tqdm import tqdm
from dotenv import load_dotenv
from groq import Groq
import backoff  


def prettify_key(key):
    key = key.replace('_', ' ')
    key = re.sub('([a-z])([A-Z])', r'\1 \2', key)
    return key.title()


def is_suspicious(s: str) -> bool:
    """Detect if a translation looks invalid (too short, punctuation only, contains English letters)."""
    if s is None:
        return True
    s = s.strip()
    if s == "":
        return True
    # too short (likely punctuation)
    if len(s) <= 2:
        return True
    # composed only of punctuation
    if all(ch in ".,;:!?-–—()[]{}\"' " for ch in s):
        return True
    return False


class JSONTranslator:
    def __init__(self, cache_file=None):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.target_language = os.getenv("DEFAULT_TARGET_LANGUAGE", "Latvian")
        self.model_name = "llama3-70b-8192"

        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY in .env")

        # Instantiate Groq client
        self.client = Groq(api_key=self.api_key)

        # use language-specific cache file
        if cache_file is None:
            cache_file = f"translation_cache_{self.target_language}.json"
        self.cache_file = cache_file
        self.translation_cache = self.load_translation_cache()

    def load_translation_cache(self):
        if os.path.isfile(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding='utf-8') as f:
                    print(f"Loaded translation cache from {self.cache_file}")
                    return json.load(f)
            except Exception as e:
                print(f"Error loading translation cache: {e}")
        return {}

    def save_translation_cache(self):
        try:
            with open(self.cache_file, "w", encoding='utf-8') as f:
                json.dump(self.translation_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving translation cache: {e}")

    @backoff.on_exception(backoff.expo, Exception, max_tries=5, jitter=None)
    def _api_translate(self, prompt):
        """Internal method to call Groq API with retries."""
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            stream=False,
        )
        return completion.choices[0].message.content.strip()

    def translate_text(self, text, context=""):
        cache_key = f"{text}_{context}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        context_part = f"Context (JSON path): {context}\n" if context else ""
        prompt = (
            f"Translate the following English text into {self.target_language}.\n"
            f"{context_part}"
            f"Only return the translation, with no additional text or explanation.\n"
            f"English: {text}\n"
            f"{self.target_language}:"
        )

        attempt = 0
        translation = None

        while attempt < 5: 
            try:
                translation = self._api_translate(prompt)

                # Print debug info for analysis
                print("\n=== TRANSLATION DEBUG ===")
                print(f"INPUT TEXT: {repr(text)}")
                print(f"CONTEXT: {repr(context)}")
                print(f"OUTPUT TEXT: {repr(translation)}")
                print("=========================\n")

                if not is_suspicious(translation):
                    break  

                print(f"[WARNING] Suspicious translation detected (attempt {attempt+1}): {repr(translation)}")
                attempt += 1

            except Exception as e:
                print(f"[ERROR] API error on attempt {attempt+1}: {e}")
                attempt += 1

        if translation is None:
            translation = text  # complete failure case

        self.translation_cache[cache_key] = translation
        self.save_translation_cache()

        return translation

    def all_strings(self, obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                yield from self.all_strings(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                yield from self.all_strings(item, f"{path}[{i}]")
        elif isinstance(obj, str):
            context = self.get_context_from_path(path)
            yield obj, context, path

    def apply_translated_strings(self, obj, translations_by_path, path=""):
        if isinstance(obj, dict):
            return {
                key: self.apply_translated_strings(value, translations_by_path, f"{path}.{key}" if path else key)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self.apply_translated_strings(item, translations_by_path, f"{path}[{i}]") for i, item in enumerate(obj)]
        elif isinstance(obj, str):
            return translations_by_path.get(path, obj)
        else:
            return obj

    def get_context_from_path(self, path):
        raw_keys = re.split(r'\.|$$|$$', path)
        tree = [prettify_key(piece) for piece in raw_keys if piece and not piece.isnumeric()]
        return ' > '.join(tree) if tree else ''

    def translate_json_file(self, input_file, output_file):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Starting translation of {input_file}...")
            print(f"Target language: {self.target_language}")

            # Find all unique string leafs & paths
            all_strs = list(self.all_strings(data))
            # Only translate the ones not cached (by text+context)
            to_process = [x for x in all_strs if f"{x[0]}_{x[1]}" not in self.translation_cache]

            print(f"Total strings to translate: {len(all_strs)}")
            print(f"Remaining to translate: {len(to_process)}")
            for text, context, path in tqdm(to_process, desc="Translating"):
                _ = self.translate_text(text, context)

            # Map paths to translations for reconstruction
            translations_by_path = {}
            for text, context, path in all_strs:
                cache_key = f"{text}_{context}"
                translations_by_path[path] = self.translation_cache.get(cache_key, text)

            translated_data = self.apply_translated_strings(data, translations_by_path)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, indent=4, ensure_ascii=False)

            print(f"Translation completed! Output saved to {output_file}")
            print(f"Total translations performed (cache size): {len(self.translation_cache)}")

        except FileNotFoundError:
            print(f"Error: File {input_file} not found.")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    INPUT_FILE = "en-US.json"  # Change as needed

    translator = JSONTranslator()
    OUTPUT_FILE = f"test_translated_{translator.target_language}.json"

    translator.translate_json_file(INPUT_FILE, OUTPUT_FILE)

    print("\nExample translations from cache:")
    for i, (key, value) in enumerate(list(translator.translation_cache.items())[:5]):

        original = key.split('_')[0]
        print(f"  {original} → {value}")
        if i >= 4:
            break
