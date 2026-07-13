# -*- coding: utf-8 -*-
# patch2.py - meal button layout fix + mobile UI
# Usage: cd ~/itochu0523.github.io/tasks && python3 patch2.py
import re, sys

with open('daily-tasks.html','r',encoding='utf-8') as f:
    h=f.read()

results=[]

# ── 1. 食事ボタンを縦積みに（横並びで文字が縦になる問題修正）──
pat=r"var row=document\.createElement\('div'\);row\.style\.cssText='display:flex;gap:8px'.*?wrap2\.appendChild\(row\);"
m=re.search(pat,h,re.DOTALL)
if m:
    new_code=(
        "var b1=mkBtn('\U0001f373','\u30e1\u30cb\u30e5\u30fc\u3092\u9078\u3076','\u30bf\u30c3\u30d7\u3057\u3066\u9078\u629e',false,'#6fcf97',onSelectFn);"
        "var eoBtn=document.createElement('button');"
        "eoBtn.style.cssText='width:100%;margin-top:8px;padding:13px;background:rgba(196,150,58,0.08);border:1px solid rgba(196,150,58,0.25);border-radius:14px;color:rgba(196,150,58,0.9);font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;min-height:50px';"
        "eoBtn.textContent='\U0001f37d\ufe0f \u5916\u98df\u3059\u308b';"
        "eoBtn.onclick=onEatoutFn;"
        "wrap2.appendChild(b1);wrap2.appendChild(eoBtn);"
    )
    h=h[:m.start()]+new_code+h[m.end():]
    results.append("meal buttons vertical")
else:
    results.append("meal buttons: already fixed or not found")

# ── 2. task-btn CSS モバイル最適化 ────────────────────────────
replacements=[
    # フォントサイズ
    ('.t-lbl{color:white;font-size:17px;font-weight:600;margin-bottom:3px;}',
     '.t-lbl{color:white;font-size:16px;font-weight:600;margin-bottom:2px;line-height:1.35;}'),
    # パディング
    ('padding:15px 16px;min-height:72px;margin-bottom:10px;',
     'padding:14px 14px;min-height:68px;margin-bottom:8px;'),
    # サブテキスト
    ('.t-sub{color:var(--muted);font-size:13px;}',
     '.t-sub{color:var(--muted);font-size:12px;line-height:1.3;}'),
    # アイコン
    ('.t-icon{width:52px;height:52px;border-radius:14px;',
     '.t-icon{width:46px;height:46px;border-radius:12px;'),
    # チェック
    ('.chk{width:36px;height:36px;','.chk{width:32px;height:32px;'),
]
for old,new in replacements:
    if old in h:
        h=h.replace(old,new)
        results.append("CSS: "+old[:30].strip())

# ── 3. 食事セクションヘッダーを小さく ────────────────────────
# 昼食/夕食のラベルスタイル調整
h=h.replace(
    "hdr.style.cssText='font-size:11px;font-weight:700;letter-spacing:1.5px;color:var(--muted);margin-bottom:6px;padding-left:2px;text-transform:uppercase'",
    "hdr.style.cssText='font-size:11px;font-weight:700;letter-spacing:1px;color:var(--muted);margin-bottom:6px;padding-left:2px;opacity:0.7'"
)

# ── 4. 食事セクション全体のマージン調整 ──────────────────────
h=h.replace(
    "wrap2.style.cssText='margin-bottom:10px'",
    "wrap2.style.cssText='margin-bottom:8px'"
)

# ── 5. クイックタスクの完了ボタンを分かりやすく ──────────────
h=h.replace(
    "'\u2713</button>'",
    "'\u2713 \u5b8c\u4e86</button>'"
)

with open('daily-tasks.html','w',encoding='utf-8') as f:
    f.write(h)

js='\n'.join(re.findall(r'<script>(.*?)</script>',h,re.DOTALL))
op,cl=js.count('{'),js.count('}')
print("Results:")
for r in results: print(" -",r)
print("Braces:","OK" if op==cl else "MISMATCH %dvs%d"%(op,cl))
print("Done! Run: git add daily-tasks.html && git commit -m 'fix: mobile UI' && git push origin main")
