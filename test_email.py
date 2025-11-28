"""Quick test for email extractor"""
import shutil
import os
from chrome_forge import PromptAnalyzer, convert_to_manifest_format
from manifest_builder import generate_manifest
from code_generator import CodeGenerator

# Clean
if os.path.exists("generated_extension"):
    shutil.rmtree("generated_extension")

# Generate
prompt = "Extract all email addresses from the current page and display them in a list."
analyzer = PromptAnalyzer(prompt)
requirements = analyzer.analyze()

print("Analysis:")
print(f"  Popup: {requirements['needs_popup']}")
print(f"  Content Script: {requirements['needs_content_script']}")

manifest_analysis = convert_to_manifest_format(requirements, prompt)
generate_manifest(manifest_analysis, out_dir="generated_extension")

generator = CodeGenerator(requirements, prompt)
files = generator.generate_all_files("generated_extension")

print("\nGenerated files:", files)
print("\n✅ Extension ready in 'generated_extension' folder")
print("\nTo test:")
print("1. Load extension in Chrome")
print("2. Visit a webpage with emails (like a contact page)")
print("3. Click extension icon")
print("4. Click 'Extract Emails' button")
print("5. Emails should appear in a list below the button")
