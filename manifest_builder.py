"""
manifest_builder.py
Part B — Manifest Builder (Manifest V3 generator)

Usage:
    - Provide an `analysis` dict (output from Part A) and call generate_manifest(analysis).
    - The script writes generated_extension/manifest.json (creates folder if missing).
"""

import json
import os
from typing import Dict, List, Any

def is_host_pattern(s: str) -> bool:
    """Rudimentary detection for host permission patterns vs normal API permissions."""
    if not isinstance(s, str):
        return False
    s = s.strip()
    # treat <all_urls> and anything containing :// or wildcard *:// or leading * as host pattern
    return (
        s == "<all_urls>"
        or "://" in s
        or s.startswith("*")
        or s.startswith("http")
        or s.startswith("https")
    )

def normalize_version(v: str) -> str:
    if not v:
        return "1.0"
    return v

def generate_manifest(analysis: Dict[str, Any], out_dir: str = "generated_extension") -> Dict[str, Any]:
    """
    Build and write a manifest.json for Manifest V3 based on analysis dict.

    Expected analysis keys (examples):
      - name: str
      - version: str
      - description: str
      - need_popup: bool
      - need_content: bool
      - need_background: bool
      - need_css: bool
      - permissions: List[str]  # may include host patterns like "<all_urls>" or "https://*.example.com/*"
      - content_matches: List[str]  # host patterns targeted by content scripts (optional)
      - icons: dict (optional)
    """
    # Basic fields with safe defaults
    name = analysis.get("name", "Generated Extension")
    version = normalize_version(analysis.get("version", "1.0"))
    description = analysis.get("description", analysis.get("desc", ""))

    need_popup = bool(analysis.get("need_popup"))
    need_content = bool(analysis.get("need_content"))
    need_background = bool(analysis.get("need_background"))
    need_css = bool(analysis.get("need_css"))

    raw_permissions: List[str] = analysis.get("permissions", []) or []
    # content_matches default
    content_matches: List[str] = analysis.get("content_matches", []) or []
    if need_content and not content_matches:
        # If content script is requested but no matches provided, default to all pages
        content_matches = ["<all_urls>"]

    # split raw_permissions into permissions (APIs) and host_permissions (URL patterns)
    permissions_list: List[str] = []
    host_permissions: List[str] = []
    for p in raw_permissions:
        if is_host_pattern(p):
            if p not in host_permissions:
                host_permissions.append(p)
        else:
            if p not in permissions_list:
                permissions_list.append(p)

    # If content_matches have host patterns, we may add them to host_permissions
    for m in content_matches:
        if is_host_pattern(m) and m not in host_permissions:
            host_permissions.append(m)

    # Construct the manifest dict
    manifest: Dict[str, Any] = {
        "manifest_version": 3,
        "name": name,
        "version": version,
        "description": description,
    }

    # icons if provided
    icons = analysis.get("icons")
    if isinstance(icons, dict) and icons:
        manifest["icons"] = icons

    # action / popup
    if need_popup:
        # manifest.action for MV3
        action_obj = {}
        default_popup = analysis.get("popup_file", "popup.html")
        action_obj["default_popup"] = default_popup
        # optionally provide a default_icon if icons included
        if icons:
            # choose 48 (fallback) if available
            if "48" in icons:
                action_obj["default_icon"] = icons["48"]
            else:
                action_obj["default_icon"] = icons
        manifest["action"] = action_obj

    # background (service worker) for MV3
    if need_background:
        service_worker = analysis.get("background_file", "background.js")
        manifest["background"] = {"service_worker": service_worker}

    # content scripts
    if need_content:
        cs_files = analysis.get("content_js", ["content.js"])
        cs_css = []
        if need_css:
            cs_css = analysis.get("content_css", ["styles.css"])
        content_entry = {
            "matches": content_matches,
            "js": cs_files
        }
        if cs_css:
            content_entry["css"] = cs_css
        manifest["content_scripts"] = [content_entry]

    # permissions (API-level)
    if permissions_list:
        manifest["permissions"] = permissions_list

    # host_permissions (URL patterns)
    if host_permissions:
        manifest["host_permissions"] = host_permissions

    # optional key for minimum Chrome extension security policy - keep default unless specified
    # Some extensions include "content_security_policy" for extension pages; leave out unless needed.

    # Final: ensure folder exists and write manifest.json
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[+] Wrote manifest to: {out_path}")
    return manifest

# ----------------------------
# Example usages / test scenarios
# ----------------------------
if __name__ == "__main__":
    examples = {
        "popup_date": {
            "name": "Today Date Popup",
            "version": "1.0",
            "description": "Shows today's date in a popup",
            "need_popup": True,
            "need_content": False,
            "need_background": False,
            "need_css": False,
            "permissions": []
        },
        "highlight_phone": {
            "name": "Phone Highlighter",
            "version": "1.0",
            "description": "Highlights phone numbers on pages",
            "need_popup": False,
            "need_content": True,
            "need_background": False,
            "need_css": True,
            "permissions": ["activeTab"],
            # content scripts will run on all pages by default
        },
        "block_sites": {
            "name": "Site Blocker",
            "version": "1.0",
            "description": "Blocks Facebook and TikTok",
            "need_popup": False,
            "need_content": False,
            "need_background": True,
            "need_css": False,
            "permissions": ["webRequest", "webRequestBlocking", "<all_urls>"]
        }
    }

    # write three manifests to subfolders for quick testing
    for key, ana in examples.items():
        outdir = os.path.join("generated_extension_examples", key)
        m = generate_manifest(ana, out_dir=outdir)
        print(f"\n== {key} manifest ==\n{json.dumps(m, indent=2)}\n")
