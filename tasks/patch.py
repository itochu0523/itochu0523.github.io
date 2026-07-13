# daily-tasks.html パッチスクリプト
# 使い方: python3 patch.py
import re, os

path = 'daily-tasks.html'
if not os.path.exists(path):
    print("ERROR: daily-tasks.html が見つかりません")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    h = f.read()

ok = []

# ── 1. State初期化 ─────────────────────────────────────────────
old = "  if(!state.mealFeedback)state.mealFeedback={};"
new = old + "\n  if(!state.quickTasks)state.quickTasks=[];\n  if(!state.lunchMeals)state.lunchMeals={};\n  if(!state.weeklyCustom)state.weeklyCustom=[];"
if old in h and "quickTasks" not in h:
    h = h.replace(old, new)
    ok.append("State init")

old2 = "      if(!rec.mealFeedback)rec.mealFeedback={};"
new2 = old2 + "\n      if(!rec.quickTasks)rec.quickTasks=[];\n      if(!rec.lunchMeals)rec.lunchMeals={};\n      if(!rec.weeklyCustom)rec.weeklyCustom=[];"
if old2 in h:
    h = h.replace(old2, new2)

# ── 2. renderAll ──────────────────────────────────────────────
h = h.replace(
    "function renderAll(){renderHome();renderDrink();renderShopTab(curShopTab);renderMealTab(curMealTab);renderStockPage();}",
    "function renderAll(){renderHome();renderDrink();renderQuickTasks();renderShopTab(curShopTab);renderMealTab(curMealTab);renderStockPage();}"
)

# ── 3. 週次タスクセクション置換 ──────────────────────────────
weekly_old = "  // 週タスク\n  renderWeeklySection();"
if weekly_old not in h:
    for pat in [
        "  // 週タスク\n  const we=document.getElementById('weekly-tasks');we.innerHTML='';\n  WEEKLY.forEach(t=>we.appendChild(mkBtn(t.e,t.l,t.s,getWeekDone(t.id),'#b08ac0',()=>toggleWeek(t.id))));",
    ]:
        if pat in h:
            h = h.replace(pat, "  // 週タスク\n  renderWeeklySection();")
            ok.append("Weekly section")
            break

# ── 4. 新機能JS挿入 ───────────────────────────────────────────
MARKER = "// \u2500\u2500\u2500 HOME \u2500"
if MARKER in h and "addQuickTask" not in h:
    NEW_JS = r"""
// ─── クイックタスク ─────────────────────────────────────────
function addQuickTask(){
  var inp=document.getElementById('qt-input');var txt=inp.value.trim();if(!txt)return;
  if(!state.quickTasks)state.quickTasks=[];
  state.quickTasks.push({id:Date.now().toString(),text:txt,done:false});
  inp.value='';saveLocal();sched();renderQuickTasks();
}
function doneQuickTask(id){
  state.quickTasks=(state.quickTasks||[]).map(function(t){return t.id===id?Object.assign({},t,{done:true}):t;});
  saveLocal();sched();renderQuickTasks();renderHome();
}
function deleteQuickTask(id){
  state.quickTasks=(state.quickTasks||[]).filter(function(t){return t.id!==id;});
  saveLocal();sched();renderQuickTasks();
}
function renderQuickTasks(){
  var el=document.getElementById('qt-list');if(!el)return;el.innerHTML='';
  var tasks=(state.quickTasks||[]).filter(function(t){return !t.done;});
  if(!tasks.length){el.innerHTML='<div style="font-size:13px;color:var(--muted);padding:6px 2px">タスクを追加してください</div>';return;}
  tasks.forEach(function(t){
    var row=document.createElement('div');
    row.style.cssText='display:flex;align-items:center;gap:10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:14px 15px;margin-bottom:8px';
    row.innerHTML='<button onclick="doneQuickTask(\''+t.id+'\')" style="width:32px;height:32px;border-radius:50%;border:2px solid var(--green);background:transparent;cursor:pointer;font-size:16px;color:var(--green);flex-shrink:0">✓</button>'
      +'<span style="flex:1;font-size:16px;color:white">'+t.text+'</span>'
      +'<button onclick="deleteQuickTask(\''+t.id+'\')" style="background:none;border:none;color:rgba(255,80,80,0.5);font-size:20px;cursor:pointer;padding:4px 8px">✕</button>';
    el.appendChild(row);
  });
}

// ─── 昼食スロット ────────────────────────────────────────────
var mealSlotTarget=null;
function getLunch(){return (state.lunchMeals||{})[todayStr()]||{menuId:null,cooked:false,eaten:false};}
function selectLunch(mealId){
  var k=todayStr();if(!state.lunchMeals)state.lunchMeals={};
  state.lunchMeals[k]={menuId:mealId,cooked:false,eaten:false};
  var meal=mealById(mealId);
  if(meal){(meal.ings||[]).forEach(function(ing){if(!fridgeHas(ing.n)&&!(state.shopMemo||[]).find(function(s){return s.text===ing.n;})){state.shopMemo=[].concat(state.shopMemo||[],[{id:'ing_'+Date.now(),text:ing.n,active:true}]);}});}
  saveLocal();sched();renderHome();mealSlotTarget=null;closeRecipe();
}
function toggleLunchCooked(){
  var k=todayStr();if(!state.lunchMeals)state.lunchMeals={};
  if(!state.lunchMeals[k])state.lunchMeals[k]={menuId:null,cooked:false,eaten:false};
  state.lunchMeals[k].cooked=!state.lunchMeals[k].cooked;
  saveLocal();sched();renderHome();
}
function toggleLunchEaten(){
  var k=todayStr();if(!state.lunchMeals)state.lunchMeals={};
  if(!state.lunchMeals[k])state.lunchMeals[k]={menuId:null,cooked:false,eaten:false};
  var was=state.lunchMeals[k].eaten;
  state.lunchMeals[k].eaten=!state.lunchMeals[k].eaten;
  saveLocal();sched();renderHome();
  if(!was&&state.lunchMeals[k].eaten&&state.lunchMeals[k].menuId)setTimeout(function(){openFb(state.lunchMeals[k].menuId);},400);
}

// ─── カスタム週次タスク ──────────────────────────────────────
function openWeeklyModal(){document.getElementById('weekly-modal').classList.add('open');}
function closeWeeklyModal(){document.getElementById('weekly-modal').classList.remove('open');}
function addWeeklyCustom(){
  var txt=document.getElementById('wc-input').value.trim();
  var emoji=document.getElementById('wc-emoji').value.trim()||'📌';
  if(!txt)return;
  if(!state.weeklyCustom)state.weeklyCustom=[];
  state.weeklyCustom.push({id:'wc_'+Date.now(),label:txt,emoji:emoji});
  document.getElementById('wc-input').value='';document.getElementById('wc-emoji').value='';
  saveLocal();sched();renderWeeklySection();closeWeeklyModal();
}
function deleteWeeklyCustom(id){
  state.weeklyCustom=(state.weeklyCustom||[]).filter(function(t){return t.id!==id;});
  Object.keys(state.weeks||{}).forEach(function(k){if(state.weeks[k])delete state.weeks[k][id];});
  saveLocal();sched();renderWeeklySection();
}
function renderWeeklySection(){
  var el=document.getElementById('weekly-tasks');if(!el)return;el.innerHTML='';
  WEEKLY.forEach(function(t){el.appendChild(mkBtn(t.e,t.l,t.s,getWeekDone(t.id),'#b08ac0',function(){toggleWeek(t.id);}));});
  (state.weeklyCustom||[]).forEach(function(t){
    var b=mkBtn(t.emoji,t.label,'週1回',getWeekDone(t.id),'#b08ac0',function(){toggleWeek(t.id);});
    b.style.position='relative';
    var del=document.createElement('button');
    del.style.cssText='position:absolute;top:50%;right:12px;transform:translateY(-50%);background:none;border:none;color:rgba(255,80,80,0.4);font-size:18px;cursor:pointer;padding:4px';
    del.textContent='✕';
    del.onclick=function(e){e.stopPropagation();deleteWeeklyCustom(t.id);};
    b.appendChild(del);el.appendChild(b);
  });
  var addBtn=document.createElement('button');
  addBtn.style.cssText='width:100%;padding:14px;background:rgba(176,138,192,0.07);border:1px dashed rgba(176,138,192,0.25);border-radius:var(--radius);color:rgba(176,138,192,0.7);font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;min-height:54px;margin-top:2px';
  addBtn.textContent='＋ タスクを追加';addBtn.onclick=openWeeklyModal;
  el.appendChild(addBtn);
}
"""
    h = h.replace(MARKER, NEW_JS + MARKER)
    ok.append("New JS inserted")

# ── 5. selectMealをスロット対応に ────────────────────────────
if "mealSlotTarget==='lunch'" not in h:
    h = h.replace(
        "function selectMeal(mealId){",
        "function selectMeal(mealId){\n  if(mealSlotTarget==='lunch'){selectLunch(mealId);return;}"
    )
    ok.append("selectMeal slot")

# ── 6. 食事セクションを昼食+夕食に変更 ──────────────────────
MEAL_OLD = "  // 食事（昼食・夕食）"
if MEAL_OLD not in h:
    targets = [
        "  // 食事 - meal=nullでもクラッシュしないように安全に処理",
        "  // 食事\n  const me=document.getElementById('meal-task')"
    ]
    for tgt in targets:
        if tgt in h:
            # 食事セクション全体を探して置換
            start = h.find(tgt)
            end = h.find("\n  // 毎日タスク", start)
            if end > start:
                OLD_SECTION = h[start:end]
                NEW_SECTION = """  // 食事（昼食・夕食）
  var me=document.getElementById('meal-task');me.innerHTML='';
  function renderMealSlot(slotLabel,slotIcon,slotTm,onSelectFn,onCookedFn,onEatenFn,onEatoutFn){
    var wrap2=document.createElement('div');wrap2.style.cssText='margin-bottom:10px';
    var hdr=document.createElement('div');hdr.style.cssText='font-size:11px;font-weight:700;letter-spacing:1.5px;color:var(--muted);margin-bottom:6px;padding-left:2px;text-transform:uppercase';
    hdr.textContent=slotIcon+' '+slotLabel;wrap2.appendChild(hdr);
    var slotMeal=slotTm.menuId?mealById(slotTm.menuId):null;
    if(slotTm.type==='eatout'){
      if(!slotTm.eaten)wrap2.appendChild(mkBtn(slotTm.emoji||'🍽️','外食: '+slotTm.eatOutName,'食べたらタップ',false,'#c4963a',onEatenFn));
      else wrap2.appendChild(mkBtn(slotTm.emoji||'🍽️','外食: '+slotTm.eatOutName,'完了',true,'#6fcf97',function(){}));
    }else if(!slotTm.menuId||!slotMeal){
      var row=document.createElement('div');row.style.cssText='display:flex;gap:8px';
      var b1=mkBtn('🍳','メニューを選ぶ','',false,'#6fcf97',onSelectFn);b1.style.flex='1';
      var b2=mkBtn('🍽️','外食','',false,'#c4963a',onEatoutFn);b2.style.minWidth='80px';
      row.appendChild(b1);row.appendChild(b2);wrap2.appendChild(row);
    }else{
      if(!slotTm.cooked)wrap2.appendChild(mkBtn(slotMeal.emoji||'🍳',slotMeal.name+'を調理','',false,'#e07b54',onCookedFn));
      else if(!slotTm.eaten)wrap2.appendChild(mkBtn(slotMeal.emoji||'🍳',slotMeal.name+'を食べる','調理完了！',false,'#c4963a',onEatenFn));
      else wrap2.appendChild(mkBtn(slotMeal.emoji||'🍳',slotMeal.name,'完了',true,'#6fcf97',function(){}));
    }
    me.appendChild(wrap2);
  }
  var lunch=getLunch();
  renderMealSlot('昼食','🌞',lunch,
    function(){mealSlotTarget='lunch';setPage('meal');},
    toggleLunchCooked,toggleLunchEaten,
    function(){mealSlotTarget='lunch';setPage('meal');mTab('eatout');});
  var tm=getTodayMeal();
  if(tm.menuId&&!mealById(tm.menuId)){var k2=todayStr();if(state.meals)state.meals[k2]={menuId:null,cooked:false,eaten:false};}
  renderMealSlot('夜ご飯','🌙',tm,
    function(){mealSlotTarget=null;setPage('meal');},
    toggleCooked,toggleEaten,
    function(){mealSlotTarget=null;setPage('meal');mTab('eatout');});"""
                h = h.replace(OLD_SECTION, NEW_SECTION)
                ok.append("Meal slots")
                break

# ── 7. リング計算修正 ─────────────────────────────────────────
h = h.replace(
    "  const total=(TRASH[dow]?1:0)+1+1+DAILY.length+shopTask+WEEKLY.length;",
    "  const total=(TRASH[dow]?1:0)+1+2+DAILY.length+shopTask+WEEKLY.length+(state.weeklyCustom||[]).length;"
)
h = h.replace(
    "  const total=(TRASH[dow]?1:0)+1+2+DAILY.length+shopTask+WEEKLY.length;",
    "  const total=(TRASH[dow]?1:0)+1+2+DAILY.length+shopTask+WEEKLY.length+(state.weeklyCustom||[]).length;"
)

# ── 8. HTMLにクイックタスクセクション追加 ───────────────────
QT_HTML = '''  <div class="sec">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
      <span class="sec-label" style="margin-bottom:0">&#9889; すぐやるタスク</span>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:10px">
      <input type="text" id="qt-input" placeholder="タスクを追加..." onkeydown="if(event.key===\'Enter\')addQuickTask()"
        style="flex:1;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:13px 15px;color:white;font-size:15px;outline:none;font-family:inherit;min-height:50px">
      <button onclick="addQuickTask()" style="background:var(--green);border:none;border-radius:14px;padding:13px 16px;color:#111a14;font-weight:700;font-size:15px;cursor:pointer;font-family:inherit;min-height:50px">&#36861;&#21152;</button>
    </div>
    <div id="qt-list"></div>
  </div>
  '''
DRINK_MARKER = '  <div class="sec"><div class="sec-label">&#128167; 今日の水分</div><div id="drink-widget"></div></div>'
if 'qt-input' not in h and DRINK_MARKER in h:
    h = h.replace(DRINK_MARKER, QT_HTML + DRINK_MARKER)
    ok.append("QT HTML")
elif 'qt-input' not in h:
    # マーカーが日本語の場合
    marker2 = '<div class="sec"><div class="sec-label">'
    idx = h.find('drink-widget')
    if idx > 0:
        sec_start = h.rfind('<div class="sec">', 0, idx)
        if sec_start > 0:
            h = h[:sec_start] + QT_HTML.replace("&#9889;","⚡").replace("&#36861;&#21152;","追加").replace("&#128167;","💧") + h[sec_start:]
            ok.append("QT HTML (fallback)")

# ── 9. 週次タスク追加モーダル ─────────────────────────────────
MODAL_HTML = """<!-- 週次タスク追加モーダル -->
<div class="ov" id="weekly-modal" onclick="if(event.target===this)closeWeeklyModal()">
  <div class="mbox">
    <div class="m-title">📅 週次タスクを追加</div>
    <div style="display:flex;gap:8px;margin-bottom:12px">
      <input type="text" id="wc-emoji" placeholder="絵文字" style="width:60px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:12px;color:white;font-size:20px;text-align:center;outline:none">
      <input type="text" id="wc-input" placeholder="タスク名" style="flex:1;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:12px 14px;color:white;font-size:15px;outline:none;font-family:inherit">
    </div>
    <div class="m-btns">
      <button class="m-btn s" onclick="closeWeeklyModal()">キャンセル</button>
      <button class="m-btn p" onclick="addWeeklyCustom()">✅ 追加</button>
    </div>
  </div>
</div>
"""
if 'weekly-modal' not in h:
    h = h.replace("<!-- 設定モーダル -->", MODAL_HTML + "<!-- 設定モーダル -->")
    ok.append("Weekly modal")

with open(path, 'w', encoding='utf-8') as f:
    f.write(h)

import re
js = '\n'.join(re.findall(r'<script>(.*?)</script>', h, re.DOTALL))
op, cl = js.count('{'), js.count('}')
print("Applied:", ', '.join(ok))
print("Braces:", op, "vs", cl, "->", "OK" if op==cl else "MISMATCH!")
print("QuickTask:", "addQuickTask" in h)
print("Lunch:", "selectLunch" in h)
print("WeeklyCustom:", "addWeeklyCustom" in h)
print("Done!")
