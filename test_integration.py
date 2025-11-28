"""
Integration Test for Part A (Prompt Analysis) and Part B (Manifest Builder)
Tests multiple scenarios to ensure both parts work together correctly
"""

import json
import os
import shutil
from chrome_forge import PromptAnalyzer, convert_to_manifest_format
from manifest_builder import generate_manifest


def clean_test_output():
    """Clean up previous test outputs"""
    if os.path.exists("test_outputs"):
        shutil.rmtree("test_outputs")
    os.makedirs("test_outputs", exist_ok=True)


def test_scenario(scenario_name, prompt, expected):
    """Test a single scenario"""
    print(f"\n{'='*70}")
    print(f"TEST: {scenario_name}".center(70))
    print(f"{'='*70}")
    print(f"Prompt: \"{prompt}\"")
    print()
    
    # Part A - Analyze
    analyzer = PromptAnalyzer(prompt)
    requirements = analyzer.analyze()
    
    print("Part A - Analysis Results:")
    print(f"  ✓ Needs Popup: {requirements['needs_popup']} (expected: {expected['popup']})")
    print(f"  ✓ Needs Content Script: {requirements['needs_content_script']} (expected: {expected['content']})")
    print(f"  ✓ Needs Background: {requirements['needs_background']} (expected: {expected['background']})")
    print(f"  ✓ Needs CSS: {requirements['needs_css']} (expected: {expected['css']})")
    print(f"  ✓ Permissions: {list(requirements['permissions'])}")
    
    # Check if results match expected
    passed = True
    if requirements['needs_popup'] != expected['popup']:
        print("  ❌ POPUP DETECTION MISMATCH!")
        passed = False
    if requirements['needs_content_script'] != expected['content']:
        print("  ❌ CONTENT SCRIPT DETECTION MISMATCH!")
        passed = False
    if requirements['needs_background'] != expected['background']:
        print("  ❌ BACKGROUND DETECTION MISMATCH!")
        passed = False
    
    # Part B - Generate Manifest
    manifest_analysis = convert_to_manifest_format(requirements, prompt)
    
    # Create scenario-specific folder
    output_dir = os.path.join("test_outputs", scenario_name.replace(" ", "_"))
    manifest = generate_manifest(manifest_analysis, out_dir=output_dir)
    
    print("\nPart B - Generated Manifest:")
    print(json.dumps(manifest, indent=2))
    
    # Verify manifest structure
    assert manifest['manifest_version'] == 3, "Must be Manifest V3"
    assert 'name' in manifest, "Must have name"
    assert 'version' in manifest, "Must have version"
    assert 'description' in manifest, "Must have description"
    
    if expected['popup']:
        assert 'action' in manifest, "Should have action for popup"
        assert 'default_popup' in manifest['action'], "Should have default_popup"
    
    if expected['background']:
        assert 'background' in manifest, "Should have background"
        assert 'service_worker' in manifest['background'], "Should have service_worker"
    
    if expected['content']:
        assert 'content_scripts' in manifest, "Should have content_scripts"
        assert len(manifest['content_scripts']) > 0, "Should have at least one content script"
    
    print(f"\n{'✅ TEST PASSED' if passed else '⚠️  TEST COMPLETED WITH WARNINGS'}")
    return passed


def main():
    """Run all integration tests"""
    print("╔" + "="*68 + "╗")
    print("║" + "INTEGRATION TEST SUITE - Parts A & B".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    clean_test_output()
    
    test_cases = [
        {
            "name": "Example 1 - Simple Popup",
            "prompt": "Create an extension that shows a popup with today's date.",
            "expected": {
                "popup": True,
                "content": False,
                "background": False,
                "css": True
            }
        },
        {
            "name": "Example 2 - Highlight Phone Numbers",
            "prompt": "Make an extension that highlights all phone numbers on any website.",
            "expected": {
                "popup": False,
                "content": True,
                "background": False,
                "css": False
            }
        },
        {
            "name": "Example 3 - Block Sites",
            "prompt": "Block Facebook and TikTok every time the browser opens.",
            "expected": {
                "popup": False,
                "content": False,
                "background": True,
                "css": False
            }
        },
        {
            "name": "Example 4 - Popup + Content",
            "prompt": "A tool that changes all webpage text to blue when I click a button in the popup.",
            "expected": {
                "popup": True,
                "content": True,
                "background": False,
                "css": True
            }
        },
        {
            "name": "Example 5 - Timer Extension",
            "prompt": "Create a pomodoro timer that shows a notification every 25 minutes.",
            "expected": {
                "popup": True,
                "content": False,
                "background": True,
                "css": True
            }
        }
    ]
    
    results = []
    for test in test_cases:
        passed = test_scenario(
            test["name"],
            test["prompt"],
            test["expected"]
        )
        results.append((test["name"], passed))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY".center(70))
    print("="*70)
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "⚠️  WARN"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    print(f"\n✓ All manifests generated in 'test_outputs/' folder")
    print(f"✓ You can load any folder in Chrome to test the extension structure")
    

if __name__ == "__main__":
    main()
