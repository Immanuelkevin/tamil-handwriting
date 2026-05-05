import re
with open('frontend/components/steps/template-download.tsx', encoding='utf-8') as f:
    text = f.read()
    m = re.search(r'const TAMIL_CHARS = \[([\s\S]*?)\]', text)
    if m:
        chars = [c.strip().strip("'").strip('"') for c in m.group(1).split(',') if c.strip() and not c.strip().startswith('//')]
        print('template-download chars:', len(chars))
        print('First 15:', chars[:15])
        print('Last 15:', chars[-15:])
