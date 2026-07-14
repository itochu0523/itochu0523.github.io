# patch4.py - fix quick task button + eatout delete
# Usage: cd ~/itochu0523.github.io/tasks && python3 patch4.py
import re

with open('daily-tasks.html','r',encoding='utf-8') as f:
    h=f.read()

# ══════════════════════════════════════════════════
# 1. クイックタスク: </script>直前に確実に関数を追加
#    (既存の壊れた定義を上書き)
# ══════════════════════════════════════════════════
QT_JS = """
// ===== QUICK TASKS (fixed) =====
window.addQuickTask=function(){
  var inp=document.getElementById('qt-input');
  if(!inp)return;
  var txt=inp.value.trim();
  if(!txt)return;
  if(!state.quickTasks)state.quickTasks=[];
  state.quickTasks.push({id:''+Date.now(),text:txt,done:false});
  inp.value='';
  saveLocal();sched();renderQuickTasks();
};
window.doneQuickTask=function(id){
  if(!state.quickTasks)return;
  state.quickTasks=state.quickTasks.map(function(t){
    return t.id===id?{id:t.id,text:t.text,done:true}:t;
  });
  saveLocal();sched();renderQuickTasks();
};
window.deleteQuickTask=function(id){
  if(!state.quickTasks)return;
  state.quickTasks=state.quickTasks.filter(function(t){return t.id!==id;});
  saveLocal();sched();renderQuickTasks();
};
window.renderQuickTasks=function(){
  var el=document.getElementById('qt-list');
  if(!el)return;
  el.innerHTML='';
  var tasks=(state.quickTasks||[]).filter(function(t){return !t.done;});
  if(!tasks.length){
    el.innerHTML='<p style="font-size:13px;color:rgba(232,245,233,0.4);padding:4px 0">'
      +'\u30bf\u30b9\u30af\u3092\u8ffd\u52a0\u3057\u3066\u304f\u3060\u3055\u3044</p>';
    return;
  }
  tasks.forEach(function(t){
    var d=document.createElement('div');
    d.style.cssText='display:flex;align-items:center;gap:10px;'
      +'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);'
      +'border-radius:14px;padding:14px;margin-bottom:8px;';
    var done=document.createElement('button');
    done.style.cssText='flex-shrink:0;min-width:70px;height:42px;border-radius:12px;'
      +'border:2px solid #6fcf97;background:rgba(111,207,151,0.1);'
      +'color:#6fcf97;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;';
    done.textContent='\u2713 \u5b8c\u4e86';
    done.onclick=(function(id){return function(){window.doneQuickTask(id);};})(t.id);
    var span=document.createElement('span');
    span.style.cssText='flex:1;font-size:16px;color:white;';
    span.textContent=t.text;
    var del=document.createElement('button');
    del.style.cssText='flex-shrink:0;background:none;border:none;'
      +'color:rgba(255,80,80,0.5);font-size:22px;cursor:pointer;padding:2px 6px;';
    del.textContent='\u2715';
    del.onclick=(function(id){return function(){window.deleteQuickTask(id);};})(t.id);
    d.appendChild(done);d.appendChild(span);d.appendChild(del);
    el.appendChild(d);
  });
};
// ===== END QUICK TASKS =====
"""

# </script>タグの直前に挿入
h = h.replace('</script>\n</body>', QT_JS + '</script>\n</body>')
if QT_JS not in h:
    h = h.replace('</script></body>', QT_JS + '</script></body>')

# ══════════════════════════════════════════════════
# 2. 外食リセット機能
# ══════════════════════════════════════════════════
EATOUT_RESET_JS = """
window.resetEatOut=function(){
  var k=todayStr();
  if(state.meals&&state.meals[k])
    state.meals[k]={menuId:null,cooked:false,eaten:false,type:null};
  saveLocal();sched();renderHome();
};
window.resetLunchEatOut=function(){
  var k=todayStr();
  if(state.lunchMeals&&state.lunchMeals[k])
    state.lunchMeals[k]={menuId:null,cooked:false,eaten:false,type:null};
  saveLocal();sched();renderHome();
};
"""
h = h.replace('// ===== END QUICK TASKS =====\n', '// ===== END QUICK TASKS =====\n' + EATOUT_RESET_JS)

# ══════════════════════════════════════════════════
# 3. 外食表示に削除ボタンを追加
#    renderMealSlot内の外食ブロックを修正
# ══════════════════════════════════════════════════

# 外食・食べた済み の表示
old_eo1 = ("else wrap2.appendChild(mkBtn(slotTm.emoji||'\U0001f37d\ufe0f',"
           "slotTm.eatOutName+'\u5b8c\u4e86','',true,'#6fcf97',function(){}));")
new_eo1 = (
    "else{"
    "wrap2.appendChild(mkBtn(slotTm.emoji||'\U0001f37d\ufe0f',slotTm.eatOutName+'\u5b8c\u4e86','',true,'#6fcf97',function(){}));"
    "var resetBtn=document.createElement('button');"
    "resetBtn.style.cssText='width:100%;margin-top:6px;padding:10px;background:transparent;"
    "border:1px dashed rgba(248,113,113,0.3);border-radius:12px;color:rgba(248,113,113,0.7);"
    "font-size:13px;cursor:pointer;font-family:inherit';"
    "resetBtn.textContent='\U0001f5d1 \u5916\u98df\u8a18\u9332\u3092\u524a\u9664';"
    "resetBtn.onclick=onResetFn||function(){};"
    "wrap2.appendChild(resetBtn);}"
)
if old_eo1 in h:
    h = h.replace(old_eo1, new_eo1)

# 外食・未食 の表示
old_eo2 = ("if(!slotTm.eaten)wrap2.appendChild(mkBtn(slotTm.emoji||'\U0001f37d\ufe0f',"
           "'\u5916\u98df: '+slotTm.eatOutName,'\u98df\u3079\u305f\u3089\u30bf\u30c3\u30d7',false,'#c4963a',onEatenFn));")
new_eo2 = (
    "if(!slotTm.eaten){"
    "wrap2.appendChild(mkBtn(slotTm.emoji||'\U0001f37d\ufe0f','\u5916\u98df: '+slotTm.eatOutName,'\u98df\u3079\u305f\u3089\u30bf\u30c3\u30d7',false,'#c4963a',onEatenFn));"
    "var cancelBtn=document.createElement('button');"
    "cancelBtn.style.cssText='width:100%;margin-top:6px;padding:10px;background:transparent;"
    "border:1px dashed rgba(248,113,113,0.3);border-radius:12px;color:rgba(248,113,113,0.7);"
    "font-size:13px;cursor:pointer;font-family:inherit';"
    "cancelBtn.textContent='\U0001f5d1 \u5916\u98df\u8a18\u9332\u3092\u524a\u9664';"
    "cancelBtn.onclick=onResetFn||function(){};"
    "wrap2.appendChild(cancelBtn);}"
)
if old_eo2 in h:
    h = h.replace(old_eo2, new_eo2)

# ══════════════════════════════════════════════════
# 4. renderMealSlot呼び出しにreset関数を渡す
# ══════════════════════════════════════════════════
# 昼食
h = re.sub(
    r'renderMealSlot\(\'\u663c\u98df\',.*?resetLunch\);',
    lambda m: m.group(0),
    h, flags=re.DOTALL
)
# resetLunchが渡されていない呼び出しを修正
def fix_lunch_call(h):
    pat = (r"renderMealSlot\('\u663c\u98df','\U0001f31e',lunch,\s*"
           r"function\(\)\{mealSlotTarget='lunch';setPage\('meal'\);\},\s*"
           r"toggleLunchCooked,toggleLunchEaten,\s*"
           r"function\(\)\{mealSlotTarget='lunch';setPage\('meal'\);mTab\('eatout'\);\}\s*\);")
    repl = ("renderMealSlot('\u663c\u98df','\U0001f31e',lunch,"
            "function(){mealSlotTarget='lunch';setPage('meal');},"
            "toggleLunchCooked,toggleLunchEaten,"
            "function(){mealSlotTarget='lunch';setPage('meal');mTab('eatout');},"
            "window.resetLunchEatOut);")
    return re.sub(pat, repl, h, flags=re.DOTALL)

def fix_dinner_call(h):
    pat = (r"renderMealSlot\('\u5915\u3054\u98df','\U0001f319',tm,\s*"
           r"function\(\)\{mealSlotTarget=null;setPage\('meal'\);\},\s*"
           r"toggleCooked,toggleEaten,\s*"
           r"function\(\)\{mealSlotTarget=null;setPage\('meal'\);mTab\('eatout'\);\}\s*\);")
    repl = ("renderMealSlot('\u5915\u3054\u98df','\U0001f319',tm,"
            "function(){mealSlotTarget=null;setPage('meal');},"
            "toggleCooked,toggleEaten,"
            "function(){mealSlotTarget=null;setPage('meal');mTab('eatout');},"
            "window.resetEatOut);")
    return re.sub(pat, repl, h, flags=re.DOTALL)

h = fix_lunch_call(h)
h = fix_dinner_call(h)

# onResetFn パラメータが関数シグネチャにない場合は追加
if 'function renderMealSlot(slotLabel,slotIcon,slotTm,onSelectFn,onCookedFn,onEatenFn,onEatoutFn)' in h:
    h = h.replace(
        'function renderMealSlot(slotLabel,slotIcon,slotTm,onSelectFn,onCookedFn,onEatenFn,onEatoutFn)',
        'function renderMealSlot(slotLabel,slotIcon,slotTm,onSelectFn,onCookedFn,onEatenFn,onEatoutFn,onResetFn)'
    )

# ══════════════════════════════════════════════════
# 5. state初期化にquickTasksを追加
# ══════════════════════════════════════════════════
if 'quickTasks' not in h.split('function loadLocal')[1][:500] if 'function loadLocal' in h else True:
    h = h.replace(
        'if(!state.mealFeedback)state.mealFeedback={};',
        'if(!state.mealFeedback)state.mealFeedback={};\n  if(!state.quickTasks)state.quickTasks=[];'
    )

# ══════════════════════════════════════════════════
# 6. renderAll に renderQuickTasks を確実に追加
# ══════════════════════════════════════════════════
if 'renderQuickTasks' not in h.split('function renderAll')[1][:100] if 'function renderAll' in h else True:
    h = h.replace(
        'function renderAll(){renderHome();',
        'function renderAll(){renderHome();if(typeof renderQuickTasks==="function")renderQuickTasks();'
    )

with open('daily-tasks.html','w',encoding='utf-8') as f:
    f.write(h)

js='\n'.join(re.findall(r'<script>(.*?)</script>',h,re.DOTALL))
op,cl=js.count('{'),js.count('}')
print("Braces:", "OK" if op==cl else "MISMATCH %dvs%d"%(op,cl))
print("addQuickTask:", "OK" if "window.addQuickTask" in h else "NG")
print("resetEatOut:", "OK" if "window.resetEatOut" in h else "NG")
print("")
print("Run: git add daily-tasks.html && git commit -m 'fix: quick task + eatout delete' && git push origin main")
