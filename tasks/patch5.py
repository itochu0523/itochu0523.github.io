# patch5.py - reliable fix via script injection
# Usage: cd ~/itochu0523.github.io/tasks && python3 patch5.py
with open('daily-tasks.html','r',encoding='utf-8') as f:
    h=f.read()

# 1. qt-input HTML が無ければ water section の前に追加
if 'qt-input' not in h:
    inject_html=(
        '<div class="sec">'
        '<div class="sec-label">\u26a1 \u3059\u3050\u3084\u308b\u30bf\u30b9\u30af</div>'
        '<div style="display:flex;gap:8px;margin-bottom:10px">'
        '<input id="qt-input" type="text"'
        ' placeholder="\u30bf\u30b9\u30af\u3092\u8ffd\u52a0..."'
        ' onkeydown="if(event.key===\'Enter\')addQuickTask()"'
        ' style="flex:1;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);'
        'border-radius:14px;padding:13px 15px;color:white;font-size:15px;outline:none;font-family:inherit;min-height:50px">'
        '<button onclick="addQuickTask()"'
        ' style="background:#6fcf97;border:none;border-radius:14px;padding:13px 16px;'
        'color:#111a14;font-weight:700;font-size:15px;cursor:pointer;font-family:inherit;min-height:50px">'
        '\u8ffd\u52a0</button>'
        '</div>'
        '<div id="qt-list"></div>'
        '</div>'
    )
    # drink-widgetの直前のsecを探して前に挿入
    idx=h.find('drink-widget')
    if idx>0:
        sec=h.rfind('<div class="sec">',0,idx)
        if sec>0:
            h=h[:sec]+inject_html+h[sec:]
            print('qt HTML added')
else:
    print('qt-input: exists')

# 2. </body>の直前にパッチスクリプトを注入
PATCH_JS=r"""
<script>
/* ===== PATCH5: quick task + eatout reset ===== */
(function(){
  /* -- quick task -- */
  window.addQuickTask=function(){
    var el=document.getElementById('qt-input');
    if(!el)return;
    var txt=el.value.trim();
    if(!txt)return;
    if(!state.quickTasks)state.quickTasks=[];
    state.quickTasks.push({id:'qt'+Date.now(),text:txt,done:false});
    el.value='';
    if(typeof saveLocal==='function')saveLocal();
    if(typeof sched==='function')sched();
    _renderQT();
  };
  window.doneQuickTask=function(id){
    if(!state.quickTasks)return;
    state.quickTasks=state.quickTasks.map(function(t){
      return t.id===id?{id:t.id,text:t.text,done:true}:t;
    });
    if(typeof saveLocal==='function')saveLocal();
    if(typeof sched==='function')sched();
    _renderQT();
  };
  window.deleteQuickTask=function(id){
    if(!state.quickTasks)return;
    state.quickTasks=state.quickTasks.filter(function(t){return t.id!==id;});
    if(typeof saveLocal==='function')saveLocal();
    if(typeof sched==='function')sched();
    _renderQT();
  };
  function _renderQT(){
    var el=document.getElementById('qt-list');
    if(!el)return;
    el.innerHTML='';
    var tasks=(state.quickTasks||[]).filter(function(t){return !t.done;});
    if(!tasks.length){
      el.innerHTML='<p style="font-size:13px;color:rgba(200,200,200,0.4);padding:4px">'
        +'\u30bf\u30b9\u30af\u3092\u8ffd\u52a0\u3057\u3066\u304f\u3060\u3055\u3044</p>';
      return;
    }
    tasks.forEach(function(t){
      var d=document.createElement('div');
      d.style.cssText='display:flex;align-items:center;gap:10px;'
        +'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);'
        +'border-radius:14px;padding:14px;margin-bottom:8px';
      var ok=document.createElement('button');
      ok.style.cssText='flex-shrink:0;min-width:72px;height:44px;border-radius:12px;'
        +'border:2px solid #6fcf97;background:rgba(111,207,151,0.1);'
        +'color:#6fcf97;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit';
      ok.textContent='\u2713 \u5b8c\u4e86';
      (function(id){ok.onclick=function(){window.doneQuickTask(id);};})(t.id);
      var sp=document.createElement('span');
      sp.style.cssText='flex:1;font-size:16px;color:white';
      sp.textContent=t.text;
      var rm=document.createElement('button');
      rm.style.cssText='flex-shrink:0;background:none;border:none;'
        +'color:rgba(255,80,80,0.5);font-size:22px;cursor:pointer;padding:2px 8px';
      rm.textContent='\xd7';
      (function(id){rm.onclick=function(){window.deleteQuickTask(id);};})(t.id);
      d.appendChild(ok);d.appendChild(sp);d.appendChild(rm);
      el.appendChild(d);
    });
  }
  window.renderQuickTasks=_renderQT;

  /* -- eatout reset -- */
  window.resetEatOut=function(){
    var k=todayStr();
    if(!state.meals)state.meals={};
    state.meals[k]={menuId:null,cooked:false,eaten:false};
    if(typeof saveLocal==='function')saveLocal();
    if(typeof sched==='function')sched();
    if(typeof renderHome==='function')renderHome();
  };
  window.resetLunchEatOut=function(){
    var k=todayStr();
    if(!state.lunchMeals)state.lunchMeals={};
    state.lunchMeals[k]={menuId:null,cooked:false,eaten:false};
    if(typeof saveLocal==='function')saveLocal();
    if(typeof sched==='function')sched();
    if(typeof renderHome==='function')renderHome();
  };

  /* -- renderHome をラップしてeatout削除ボタンを追加 -- */
  function _patchMealDiv(){
    var k=todayStr();
    var tm=(state.meals||{})[k]||{};
    var lm=(state.lunchMeals||{})[k]||{};
    var me=document.getElementById('meal-task');
    if(!me)return;
    // 既存の削除ボタンを除去（重複防止）
    me.querySelectorAll('.p5-del-btn').forEach(function(b){b.remove();});
    function makeDelBtn(labelText,onclickFn){
      var b=document.createElement('button');
      b.className='p5-del-btn';
      b.style.cssText='width:100%;margin-top:6px;padding:11px;background:transparent;'
        +'border:1px dashed rgba(248,113,113,0.35);border-radius:12px;'
        +'color:rgba(248,113,113,0.75);font-size:13px;cursor:pointer;font-family:inherit';
      b.textContent=labelText;
      b.onclick=onclickFn;
      return b;
    }
    if(tm.type==='eatout'){
      me.appendChild(makeDelBtn(
        '\u2715 \u5915\u98df\u306e\u5916\u98df\u8a18\u9332\u3092\u524a\u9664',
        window.resetEatOut
      ));
    }
    if(lm.type==='eatout'){
      me.appendChild(makeDelBtn(
        '\u2715 \u663c\u98df\u306e\u5916\u98df\u8a18\u9332\u3092\u524a\u9664',
        window.resetLunchEatOut
      ));
    }
  }

  /* renderHome が定義されるまで待ってからラップ */
  function _wrap(){
    if(typeof renderHome!=='function'||typeof state==='undefined'){
      setTimeout(_wrap,200);return;
    }
    var _orig=renderHome;
    window.renderHome=function(){
      _orig();
      _renderQT();
      _patchMealDiv();
    };
    /* renderAll もラップ */
    if(typeof renderAll==='function'){
      var _origAll=renderAll;
      window.renderAll=function(){
        _origAll();
        _renderQT();
      };
    }
    /* 初回実行 */
    _renderQT();
    _patchMealDiv();
  }
  setTimeout(_wrap,300);
})();
</script>
"""

# </body>の直前に注入
if '</body>' in h:
    h=h.replace('</body>',PATCH_JS+'\n</body>')
    print('script injected before </body>')
else:
    h=h+PATCH_JS
    print('script appended (no </body> found)')

with open('daily-tasks.html','w',encoding='utf-8') as f:
    f.write(h)

import re
js='\n'.join(re.findall(r'<script>(.*?)</script>',h,re.DOTALL))
op,cl=js.count('{'),js.count('}')
print('Braces:','OK' if op==cl else 'MISMATCH %dvs%d'%(op,cl))
print('addQuickTask:','OK' if 'window.addQuickTask' in h else 'NG')
print('resetEatOut:','OK' if 'window.resetEatOut' in h else 'NG')
print('')
print('git add daily-tasks.html && git commit -m "fix: quick task + eatout reset" && git push origin main')
