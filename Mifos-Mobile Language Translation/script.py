import os
import json
import re
from tqdm import tqdm
from dotenv import load_dotenv
from groq import Groq
import backoff  # for retry/backoff
import xml.etree.ElementTree as ET
from xml.dom import minidom


def prettify_key(key):
    key = key.replace('_', ' ')
    key = re.sub('([a-z])([A-Z])', r'\1 \2', key)
    return key.title()


def is_suspicious(s: str) -> bool:
    if s is None:
        return True
    s = s.strip()
    if s == "":
        return True
    if len(s) <= 2:
        return True
    if all(ch in ".,;:!?-–—()[]{}\"' " for ch in s):
        return True
    return False


# Load environment variables first
load_dotenv()

os.environ["DEFAULT_TARGET_LANGUAGE"] = "Polish"


class XMLTranslator:
    def __init__(self, cache_file="translation_cache_polish.json"):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.target_language = os.getenv("DEFAULT_TARGET_LANGUAGE", "Polish")
        self.model_name = "openai/gpt-oss-120b"

        if not self.api_key:
            raise ValueError("Missing GROQ_API_KEY in .env")


        self.client = Groq(api_key=self.api_key)

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

        context_part = f"Context (XML path): {context}\n" if context else ""
        prompt = (
            f"Translate the following English text into {self.target_language}.\n"
            f"{context_part}"
            f"Only return the translation, with no additional text or explanation.\n"
            f"English: {text}\n"
            f"{self.target_language}:"
        )

        attempt = 0
        translation = None

        while attempt < 5:  # manual retry loop
            try:
                translation = self._api_translate(prompt)


                print("\n=== TRANSLATION DEBUG ===")
                print(f"INPUT TEXT: {repr(text)}")
                print(f"CONTEXT: {repr(context)}")
                print(f"OUTPUT TEXT: {repr(translation)}")
                print("=========================\n")

                if not is_suspicious(translation):
                    break  # valid translation, stop retrying

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

    def parse_xml_file(self, xml_file):

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            strings = {}
            

            for string_elem in root.findall(".//string"):
                name = string_elem.get("name")
                translatable = string_elem.get("translatable", "true")
                
                if name and translatable != "false":
                    text = string_elem.text or ""
                    strings[name] = {
                        "text": text,
                        "type": "string",
                        "element": string_elem
                    }
            
            # Handle <string-array> elements
            for array_elem in root.findall(".//string-array"):
                name = array_elem.get("name")
                translatable = array_elem.get("translatable", "true")
                
                if name and translatable != "false":
                    items = []
                    for item_elem in array_elem.findall("item"):
                        item_text = item_elem.text or ""
                        items.append({
                            "text": item_text,
                            "element": item_elem
                        })
                    
                    strings[name] = {
                        "items": items,
                        "type": "string-array",
                        "element": array_elem
                    }
            
            return strings, root
            
        except Exception as e:
            print(f"Error parsing XML file {xml_file}: {e}")
            return {}, None

    def get_translatable_strings(self, english_strings, target_strings):
        translatable = {}
        
        for name in english_strings:
            if name in target_strings:
                english_entry = english_strings[name]
                target_entry = target_strings[name]
                
                if english_entry["type"] == "string" and target_entry["type"] == "string":
                    context = f"string[@name='{name}']"
                    translatable[name] = {
                        "english_text": english_entry["text"],
                        "target_element": target_entry["element"],
                        "context": context,
                        "type": "string"
                    }
                
                elif english_entry["type"] == "string-array" and target_entry["type"] == "string-array":

                    english_items = english_entry["items"]
                    target_items = target_entry["items"]
                    
                    translatable_items = []
                    max_items = min(len(english_items), len(target_items))
                    
                    for i in range(max_items):
                        context = f"string-array[@name='{name}']/item[{i}]"
                        translatable_items.append({
                            "english_text": english_items[i]["text"],
                            "target_element": target_items[i]["element"],
                            "context": context,
                            "index": i
                        })
                    
                    if translatable_items:
                        translatable[name] = {
                            "items": translatable_items,
                            "type": "string-array"
                        }
        
        return translatable

    def translate_xml_files(self, english_file, target_file, output_file):
        try:
            print(f"Starting translation of {english_file} -> {target_file}...")
            print(f"Target language: {self.target_language}")

            # Parse both XML files
            english_strings, english_root = self.parse_xml_file(english_file)
            target_strings, target_root = self.parse_xml_file(target_file)

            if not english_strings or not target_strings:
                print("Error: Could not parse XML files")
                return

            print(f"English strings found: {len(english_strings)}")
            print(f"Target strings found: {len(target_strings)}")

            # Get strings that need translation
            translatable_strings = self.get_translatable_strings(english_strings, target_strings)
            print(f"Common translatable strings: {len(translatable_strings)}")

            # Count total items to translate
            total_items = 0
            for name, entry in translatable_strings.items():
                if entry["type"] == "string":
                    total_items += 1
                elif entry["type"] == "string-array":
                    total_items += len(entry["items"])

            # Find items not in cache
            to_process = []
            for name, entry in translatable_strings.items():
                if entry["type"] == "string":
                    cache_key = f"{entry['english_text']}_{entry['context']}"
                    if cache_key not in self.translation_cache:
                        to_process.append((entry['english_text'], entry['context']))
                elif entry["type"] == "string-array":
                    for item in entry["items"]:
                        cache_key = f"{item['english_text']}_{item['context']}"
                        if cache_key not in self.translation_cache:
                            to_process.append((item['english_text'], item['context']))

            print(f"Total items to translate: {total_items}")
            print(f"Remaining to translate: {len(to_process)}")


            for text, context in tqdm(to_process, desc="Translating"):
                self.translate_text(text, context)


            for name, entry in translatable_strings.items():
                if entry["type"] == "string":
                    cache_key = f"{entry['english_text']}_{entry['context']}"
                    translation = self.translation_cache.get(cache_key, entry['english_text'])
                    entry["target_element"].text = translation
                
                elif entry["type"] == "string-array":
                    for item in entry["items"]:
                        cache_key = f"{item['english_text']}_{item['context']}"
                        translation = self.translation_cache.get(cache_key, item['english_text'])
                        item["target_element"].text = translation


            self.write_pretty_xml(target_root, output_file)

            print(f"Translation completed! Output saved to {output_file}")
            print(f"Total translations performed (cache size): {len(self.translation_cache)}")

        except Exception as e:
            print(f"Unexpected error: {e}")

    def write_pretty_xml(self, root, output_file):

        try:

            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)

            pretty_string = reparsed.toprettyxml(indent="    ")

            lines = [line for line in pretty_string.splitlines() if line.strip()]
            pretty_string = '\n'.join(lines)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pretty_string)
                
        except Exception as e:
            print(f"Error writing XML file: {e}")
            # Fallback to basic write
            tree = ET.ElementTree(root)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)

import os

def collect_translation_files(repo_root, source_folder="values-fr"):
    file_pairs = []
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            if file == "strings.xml" and source_folder in root:
                target_path = os.path.join(root, file)
                english_path = target_path.replace(source_folder, "values")
                output_path = target_path.replace(source_folder, f"{source_folder}-auto")

                if os.path.exists(english_path):
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    file_pairs.append((english_path, target_path, output_path))

    with open("file_pairs.json", "w", encoding='utf-8') as f:
        json.dump(file_pairs, f, indent=2, ensure_ascii=False)
    print(f"Collected {len(file_pairs)} file pairs for translation.")
    return file_pairs

def translate_repo(repo_root, source_folder="values-fr", target_language="Polish", cache_file=None):
    os.environ["DEFAULT_TARGET_LANGUAGE"] = target_language
    
    if cache_file is None:
        cache_file = f"translation_cache_{target_language.lower()}.json"

    translator = XMLTranslator(cache_file=cache_file)

    file_pairs = collect_translation_files(repo_root, source_folder)
    print(f"Found {len(file_pairs)} translation pairs for {source_folder} → {target_language}")

    from tqdm import tqdm
    for english_file, target_file, output_file in tqdm(file_pairs, desc="Processing files"):
        print(f"\n=== Processing ===\nEN: {english_file}\nTG: {target_file}\nOUT: {output_file}\n")
        translator.translate_xml_files(english_file, target_file, output_file)


if __name__ == "__main__":
    repo_root = "./app"   # path to your cloned repo

    translate_repo(
        repo_root,
        source_folder="values-ar", 
        target_language="Arabic"
    )