# -*- coding: utf-8 -*-
# patch3.py
# Usage: cd ~/itochu0523.github.io/tasks && python3 patch3.py
import re

with open('daily-tasks.html','r',encoding='utf-8') as f:
    h=f.read()

results=[]

# ══════════════════════════════════════════════════════
# 1. クイックタスク追加ボタンが押せない問題
#    → addQuickTask関数が存在するか確認して修正
# ══════════════════════════════════════════════════════

# qt-input が HTML に存在するか確認
if 'qt-input' not in h:
    # セクション追加（水分セクションの前に挿入）
    drink_sec='<div class="sec"><div class="sec-label">'
    drink_idx=h.find('drink-widget')
    if drink_idx>0:
        sec_start=h.rfind('<div class="sec">',0,drink_idx)
        qt_html=(
            '<div class="sec">'
            '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">'
            '<span class="sec-label" style="margin-bottom:0">\u26a1 \u3059\u3050\u3084\u308b\u30bf\u30b9\u30af</span>'
            '</div>'
            '<div style="display:flex;gap:8px;margin-bottom:10px">'
            '<input type="text" id="qt-input" placeholder="\u30bf\u30b9\u30af\u3092\u8ffd\u52a0..." '
            'onkeydown="if(event.key===\'Enter\')addQuickTask()" '
            'style="flex:1;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);'
            'border-radius:14px;padding:13px 15px;color:white;font-size:15px;outline:none;font-family:inherit;min-height:50px">'
            '<button onclick="addQuickTask()" '
            'style="background:var(--green);border:none;border-radius:14px;padding:13px 16px;'
            'color:#111a14;font-weight:700;font-size:15px;cursor:pointer;font-family:inherit;min-height:50px">'
            '\u8ffd\u52a0</button>'
            '</div>'
            '<div id="qt-list"></div>'
            '</div>'
        )
        h=h[:sec_start]+qt_html+h[sec_start:]
        results.append("qt-input HTML added")
else:
    results.append("qt-input: already exists")

# addQuickTask 関数が存在するか確認
if 'function addQuickTask' not in h:
    qt_js=(
        '\n// quick tasks\n'
        'function addQuickTask(){'
        'var inp=document.getElementById(\'qt-input\');'
        'var txt=inp.value.trim();if(!txt)return;'
        'if(!state.quickTasks)state.quickTasks=[];'
        'state.quickTasks.push({id:Date.now().toString(),text:txt,done:false});'
        'inp.value=\'\';saveLocal();sched();renderQuickTasks();'
        '}\n'
        'function doneQuickTask(id){'
        'state.quickTasks=(state.quickTasks||[]).map(function(t){'
        'return t.id===id?Object.assign({},t,{done:true}):t;});'
        'saveLocal();sched();renderQuickTasks();'
        '}\n'
        'function deleteQuickTask(id){'
        'state.quickTasks=(state.quickTasks||[]).filter(function(t){return t.id!==id;});'
        'saveLocal();sched();renderQuickTasks();'
        '}\n'
        'function renderQuickTasks(){'
        'var el=document.getElementById(\'qt-list\');if(!el)return;el.innerHTML=\'\';'
        'var tasks=(state.quickTasks||[]).filter(function(t){return !t.done;});'
        'if(!tasks.length){'
        'el.innerHTML=\'<div style="font-size:13px;color:var(--muted);padding:6px 2px">'
        '\u30bf\u30b9\u30af\u3092\u8ffd\u52a0\u3057\u3066\u304f\u3060\u3055\u3044</div>\';return;}'
        'tasks.forEach(function(t){'
        'var row=document.createElement(\'div\');'
        'row.style.cssText=\'display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.04);'
        'border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px 15px;margin-bottom:8px\';'
        'row.innerHTML=\'<button onclick="doneQuickTask(\\\'\'+t.id+\'\\\')" \''
        '+\'style="min-width:64px;height:40px;border-radius:12px;border:1px solid var(--green);'
        'background:rgba(111,207,151,0.1);cursor:pointer;font-family:inherit;'
        'color:var(--green);font-size:13px;font-weight:600;flex-shrink:0">\u2713 \u5b8c\u4e86</button>\''
        '+\'<span style="flex:1;font-size:16px;color:white">\'+t.text+\'</span>\''
        '+\'<button onclick="deleteQuickTask(\\\'\'+t.id+\'\\\')" \''
        '+\'style="background:none;border:none;color:rgba(255,80,80,0.5);font-size:20px;cursor:pointer;padding:4px 8px">\u2715</button>\';'
        'el.appendChild(row);});'
        '}\n'
    )
    # renderAll の前に挿入
    h=h.replace('function renderAll(){',qt_js+'function renderAll(){')
    results.append("addQuickTask JS added")
else:
    results.append("addQuickTask: already exists")

# renderAll に renderQuickTasks を追加
if 'renderQuickTasks' not in h.split('function renderAll()')[1][:100] if 'function renderAll()' in h else True:
    h=h.replace(
        'function renderAll(){renderHome();renderDrink();',
        'function renderAll(){renderHome();renderDrink();renderQuickTasks();'
    )

# state初期化
if 'state.quickTasks' not in h:
    h=h.replace(
        'if(!state.mealFeedback)state.mealFeedback={};',
        'if(!state.mealFeedback)state.mealFeedback={};\n  if(!state.quickTasks)state.quickTasks=[];'
    )

# ══════════════════════════════════════════════════════
# 2. 今日の食事を変更できるようにする
#    → 選択済みのとき「変更する」ボタンを追加
# ══════════════════════════════════════════════════════

# resetMeal / resetLunch 関数追加
if 'function resetMeal' not in h:
    reset_js=(
        '\nfunction resetMeal(){'
        'var k=todayStr();if(state.meals)state.meals[k]={menuId:null,cooked:false,eaten:false};'
        'saveLocal();sched();renderHome();'
        '}\n'
        'function resetLunch(){'
        'var k=todayStr();if(state.lunchMeals)state.lunchMeals[k]={menuId:null,cooked:false,eaten:false};'
        'saveLocal();sched();renderHome();'
        '}\n'
    )
    h=h.replace('function renderAll(){',reset_js+'function renderAll(){')
    results.append("resetMeal/resetLunch added")

# 食事スロット描画に「変更する」ボタンを追加
# 完了時（done状態）に変更ボタンを表示
change_btn_lunch=(
    "wrap2.appendChild(mkBtn(slotMeal.emoji||'\U0001f373',slotMeal.name+'\u5b8c\u4e86','',true,'#6fcf97',function(){}));"
)
change_btn_lunch_new=(
    "wrap2.appendChild(mkBtn(slotMeal.emoji||'\U0001f373',slotMeal.name+'\u5b8c\u4e86','',true,'#6fcf97',function(){}));"
    "var chBtn=document.createElement('button');"
    "chBtn.style.cssText='width:100%;margin-top:6px;padding:10px;background:transparent;border:1px dashed rgba(255,255,255,0.15);border-radius:12px;color:var(--muted);font-size:13px;cursor:pointer;font-family:inherit';"
    "chBtn.textContent='\U0001f504 \u30e1\u30cb\u30e5\u30fc\u3092\u5909\u66f4\u3059\u308b';"
    "chBtn.onclick=onResetFn;wrap2.appendChild(chBtn);"
)

# renderMealSlot の呼び出しにリセット関数を追加
# まず関数シグネチャを更新
if 'onResetFn' not in h:
    # renderMealSlot 関数定義にonResetFn引数を追加
    h=h.replace(
        'function renderMealSlot(slotLabel,slotIcon,slotTm,onSelectFn,onCookedFn,onEatenFn,onEatoutFn){',
        'function renderMealSlot(slotLabel,slotIcon,slotTm,onSelectFn,onCookedFn,onEatenFn,onEatoutFn,onResetFn){'
    )
    # done状態の表示に変更ボタン追加
    h=h.replace(
        "else wrap2.appendChild(mkBtn(slotMeal.emoji||'\U0001f373',slotMeal.name+'\u5b8c\u4e86','',true,'#6fcf97',function(){}));",
        "else{"
        "wrap2.appendChild(mkBtn(slotMeal.emoji||'\U0001f373',slotMeal.name+'\u5b8c\u4e86','',true,'#6fcf97',function(){}));"
        "if(onResetFn){var chBtn=document.createElement('button');"
        "chBtn.style.cssText='width:100%;margin-top:6px;padding:10px;background:transparent;border:1px dashed rgba(255,255,255,0.15);border-radius:12px;color:var(--muted);font-size:13px;cursor:pointer;font-family:inherit';"
        "chBtn.textContent='\U0001f504 \u30e1\u30cb\u30e5\u30fc\u3092\u5909\u66f4\u3059\u308b';"
        "chBtn.onclick=onResetFn;wrap2.appendChild(chBtn);}}"
    )
    # 調理中/食事中状態にも変更ボタン（小さめ）
    h=h.replace(
        "if(!slotTm.cooked)wrap2.appendChild(mkBtn(slotMeal.emoji||'\U0001f373',slotMeal.name+'\u3092\u8abf\u7406','',false,'#e07b54',onCookedFn));",
        "if(!slotTm.cooked){"
        "wrap2.appendChild(mkBtn(slotMeal.emoji||'\U0001f373',slotMeal.name+'\u3092\u8abf\u7406','',false,'#e07b54',onCookedFn));"
        "if(onResetFn){var chBtn2=document.createElement('button');"
        "chBtn2.style.cssText='width:100%;margin-top:4px;padding:8px;background:transparent;border:1px dashed rgba(255,255,255,0.12);border-radius:10px;color:var(--muted);font-size:12px;cursor:pointer;font-family:inherit';"
        "chBtn2.textContent='\u5909\u66f4\u3059\u308b';chBtn2.onclick=onResetFn;wrap2.appendChild(chBtn2);}}"
    )
    # 昼食の呼び出しにresetLunchを追加
    h=h.replace(
        'renderMealSlot(\'\u663c\u98df\',\'\U0001f31e\',lunch,\n    function(){mealSlotTarget=\'lunch\';setPage(\'meal\');},\n    toggleLunchCooked,toggleLunchEaten,\n    function(){mealSlotTarget=\'lunch\';setPage(\'meal\');mTab(\'eatout\');});',
        'renderMealSlot(\'\u663c\u98df\',\'\U0001f31e\',lunch,\n    function(){mealSlotTarget=\'lunch\';setPage(\'meal\');},\n    toggleLunchCooked,toggleLunchEaten,\n    function(){mealSlotTarget=\'lunch\';setPage(\'meal\');mTab(\'eatout\');},\n    resetLunch);'
    )
    # 夕食の呼び出しにresetMealを追加
    h=h.replace(
        'renderMealSlot(\'\u5915\u3054\u98ef\',\'\U0001f319\',tm,\n    function(){mealSlotTarget=null;setPage(\'meal\');},\n    toggleCooked,toggleEaten,\n    function(){mealSlotTarget=null;setPage(\'meal\');mTab(\'eatout\');});',
        'renderMealSlot(\'\u5915\u3054\u98ef\',\'\U0001f319\',tm,\n    function(){mealSlotTarget=null;setPage(\'meal\');},\n    toggleCooked,toggleEaten,\n    function(){mealSlotTarget=null;setPage(\'meal\');mTab(\'eatout\');},\n    resetMeal);'
    )
    results.append("meal change button added")
else:
    results.append("meal change: already exists")

with open('daily-tasks.html','w',encoding='utf-8') as f:
    f.write(h)

js='\n'.join(re.findall(r'<script>(.*?)</script>',h,re.DOTALL))
op,cl=js.count('{'),js.count('}')
print("Results:")
for r in results: print(" -",r)
print("Braces:","OK" if op==cl else "MISMATCH %dvs%d"%(op,cl))
print("")
print("Next: git add daily-tasks.html && git commit -m 'fix: quick task + meal change' && git push origin main")
