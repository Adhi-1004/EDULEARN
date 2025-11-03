#!/usr/bin/env python3

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.gemini_coding_service import GeminiCodingService

async def test_gemini_templates():
    print('Testing Gemini AI Template Generation...')
    print('=' * 50)

    service = GeminiCodingService()

    # Test fallback templates first
    fallback_templates = service._get_default_templates()
    print(f'[OK] Fallback templates available for {len(fallback_templates)} languages:')
    for lang in fallback_templates:
        print(f'  - {lang}')

    print()

    # Test if Gemini can generate a problem with templates
    try:
        print('Generating test problem with templates...')
        problem = await service.generate_coding_problem(
            topic='Array Sum',
            difficulty='easy',
            user_skill_level='beginner'
        )

        print(f'[OK] Problem generated: {problem.get("title", "Unknown")}')

        if 'code_templates' in problem:
            print(f'[OK] AI generated templates for {len(problem["code_templates"])} languages:')
            for lang in problem['code_templates']:
                template_lines = problem['code_templates'][lang].split('\n')[:3]  # First 3 lines
                template_preview = ' | '.join(template_lines)
                print(f'  - {lang}: {template_preview}...')
        else:
            print('[ERROR] AI did not generate code_templates field')
            return False

        # Verify all expected languages are present
        expected_langs = ['python', 'javascript', 'java', 'cpp', 'c']
        missing_langs = []
        for lang in expected_langs:
            if lang not in problem['code_templates']:
                missing_langs.append(lang)

        if missing_langs:
            print(f'[WARN] Missing templates for: {missing_langs}')
        else:
            print('[OK] All expected language templates present')

        return True

    except Exception as e:
        print(f'[ERROR] Gemini generation failed: {e}')
        print('Using fallback templates instead')
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_templates())
    print()
    if success:
        print('🎉 Template generation test PASSED')
    else:
        print('❌ Template generation test FAILED')
    sys.exit(0 if success else 1)
