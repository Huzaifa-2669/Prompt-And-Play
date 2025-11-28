import os
import shutil
from pathlib import Path

import pytest

from code_generator import CodeGenerator


def test_generate_files_with_gemini_success(tmp_path, monkeypatch):
    """When the Gemini client returns a proper mapping, generator should write files."""
    # Fake gemini map
    fake_map = {
        'popup.html': '<html><body>AI POPUP</body></html>',
        'popup.js': "console.log('ai popup');",
        'content.js': "console.log('ai content');",
        'styles.css': 'body { color: red; }'
    }

    # Patch the local imported reference
    import code_generator

    monkeypatch.setattr(code_generator, 'gemini_generate_files', lambda r, p: fake_map)

    requirements = {
        'needs_popup': True,
        'needs_content_script': True,
        'needs_background': False,
        'needs_css': True,
        'permissions': set(),
        'use_gemini': True
    }

    out_dir = tmp_path / 'generated_extension'
    cg = CodeGenerator(requirements, 'Make a small UI and content script')
    files = cg.generate_all_files(str(out_dir))

    assert set(files) == set(fake_map.keys())

    # Validate file contents written
    for fname, content in fake_map.items():
        written = (out_dir / fname).read_text(encoding='utf-8')
        assert content == written


def test_gemini_failure_fallback(tmp_path, monkeypatch):
    """If Gemini client fails, generator should fall back to built-in generation."""
    import code_generator

    def raise_err(r, p):
        raise RuntimeError('simulated AI failure')

    monkeypatch.setattr(code_generator, 'gemini_generate_files', raise_err)

    requirements = {
        'needs_popup': True,
        'needs_content_script': True,
        'needs_background': False,
        'needs_css': True,
        'permissions': set(),
        'use_gemini': True
    }

    out_dir = tmp_path / 'generated_extension'
    cg = CodeGenerator(requirements, 'Make a small UI and content script')
    files = cg.generate_all_files(str(out_dir))

    # The fallback generator should have created the typical files
    assert 'popup.html' in files
    assert 'popup.js' in files
    assert 'content.js' in files
    assert 'styles.css' in files
