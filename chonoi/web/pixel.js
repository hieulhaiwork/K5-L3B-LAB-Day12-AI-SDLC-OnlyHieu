"use strict";

// Art and animation consume snapshots. Coordinates, hit boxes and timers stay in the simulation.
const Pixel = (() => {
  const art = document.createElement("canvas");
  const background = art.getContext("2d");
  let backgroundKey = "";
  const normal = {
    sky: "#ffd7a0", cloud: "#fff0bd", sun: "#fff3ad", land: "#64896a", trees: "#315f52",
    water: ["#67ae9c", "#488b85", "#336f76", "#285561"], foam: "#a0d3b1", mud: "#2d5b54",
    night: "#203e4c", shadow: "#2b2835", wood: "#c89160", plank: "#b57952",
    beam: "#784936", roof: "#9d5147", light: "#ffd583", ink: "#282c35",
  };
  const high = {
    ...normal, sky:"#15192b", cloud:"#575b77", sun:"#fff0a3", land:"#424a60", trees:"#a1d894",
    water:["#173b4d","#132c42","#10263d","#0b1e30"], foam:"#62c7d8", mud:"#18404e",
    night:"#0b1624", shadow:"#000913", wood:"#38445c", plank:"#4f5d79",
    beam:"#91a6bb", roof:"#723d61", light:"#ffdf79", ink:"#070e19",
  };
  const HERO = [
    "   SSSS   ", "  SHHHHS  ", "  HKKKKH  ", "  KEEEEK  ", "   EEEE   ",
    "  MMMMMX  ", " EMTMMME  ", " EMTMMME  ", "   MMM    ", "  PPPPP   ",
    "  PP PP   ", "  BB BB   ",
  ];
  const GUEST = [
    "  SSSSS   ", " SSSSSSS  ", "SSSSSSSSS ", "  HEEEH   ", "  EEE E   ",
    "  MMMMM   ", " EMMMMME  ", "  MMMMM   ", "  PP PP   ", "  BB BB   ",
  ];
  const FISH = [
    "       L      ", " T    LDDL    ", " TTLDDDDDLL   ", " TTDDDDDEDDL  ",
    " T   LDDDLL   ", "      LDD     ",
  ];
  const CROCODILE = [
    "         L L  L        ", " T      LLLLLLL  EE    ", " TTDLLLLLLLLLLLLLDDLLL ",
    "  TTDDDDDDDDDDDDDDDDLL ", "   TDDDDDDDDDDDDDDDDDD ", "       DDD  DDD        ",
    "      DD     DD        ",
  ];
  const COLORS = ["#e3d6a1","#758d66","#dfa799","#98c2a4"];
  const FISH_COLORS = {
    ca_linh:["#dfedc1","#9cc59c","#5b9281"], ca_loc:["#ced694","#7f995a","#526954"],
    ca_keo:["#ffc37d","#c08260","#8b5756"],
  };
  const FLOWERS = { bong_dien_dien:"#ffdb65", bong_sung:"#ec99b3", keo_neo:"#b4d98a" };
  function rect(ctx, x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(Math.round(x), Math.round(y), Math.max(0, Math.round(w)), Math.max(0, Math.round(h)));
  }
  function stamp(ctx, shape, map, x, y, flip = false) {
    const width = shape[0].length;
    const left = Math.round(x - width / 2), top = Math.round(y - shape.length / 2);
    shape.forEach((row, dy) => {
      const line = flip ? [...row].reverse().join("") : row;
      for (let i = 0; i < line.length;) {
        const code = line[i];
        let end = i + 1;
        while (line[end] === code) end++;
        if (map[code]) rect(ctx, left + i, top + dy, end - i, 1, map[code]);
        i = end;
      }
    });
  }
  function sun(ctx, x, y, p) {
    rect(ctx,x-6,y-11,13,22,p.sun); rect(ctx,x-9,y-8,19,16,p.sun); rect(ctx,x-11,y-5,23,10,p.sun);
  }
  function palm(ctx, x, base, p, flip) {
    for (let i = 0; i < 5; i++) rect(ctx,x+i*(flip?-1:1),base-4-i*4,2,5,p.trees);
    const c=x+(flip?-4:4), y=base-22;
    for (const [dx,dy,w] of [[-11,-3,9],[3,-3,10],[-8,-1,17],[-3,-6,3],[-13,0,4],[9,1,4],[-7,2,5],[4,2,4]]) {
      rect(ctx,c+dx,y+dy,w,2,p.trees);
    }
  }
  function hut(ctx, x, y, p) {
    rect(ctx,x+3,y-17,28,17,p.shadow); rect(ctx,x+4,y-15,26,10,p.wood);
    rect(ctx,x+10,y-13,5,8,p.beam); rect(ctx,x+21,y-13,5,5,p.light);
    rect(ctx,x+5,y-5,2,7,p.beam); rect(ctx,x+27,y-5,2,7,p.beam);
    for (let i=0;i<7;i++) rect(ctx,x+i*2,y-17-i,35-i*4,1,i%2?p.roof:p.beam);
    rect(ctx,x-3,y,45,2,p.wood); rect(ctx,x-1,y+2,39,2,p.beam);
  }
  function riverBackground(ctx, w, h, shore, p) {
    rect(ctx,0,0,w,shore,p.sky);
    sun(ctx,Math.floor(w*.7),Math.floor(shore*.38),p);
    for (let i=0;i<6;i++) {
      const x=Math.round(w*(i+.4)/6), y=7+i%3*5;
      rect(ctx,x,y,14+i%2*7,3,p.cloud); rect(ctx,x+4,y-2,8,2,p.cloud);
    }
    for (let i=0;i<12;i++) {
      const x=Math.floor(i*w/12), y=shore-8-i%3*2;
      rect(ctx,x,y,Math.ceil(w/12)+1,shore-y,p.land);
      rect(ctx,x+3,y-4,10+i%3*3,4,p.land);
    }
    for (let i=0;i<7;i++) palm(ctx,Math.round((i+.3)*w/7),shore-2,p,i%2);
    const waterHeight=h-shore;
    for(let i=0;i<4;i++) rect(ctx,0,shore+i*waterHeight/4,w,Math.ceil(waterHeight/4)+1,p.water[i]);
    for (let i=0;i<24;i++) {
      const x=(i*47+9)%w, y=h-(i*11%9);
      rect(ctx,x,y,9+i%4*2,h-y,p.mud);
      rect(ctx,x+1,y-2,5,i%3+1,p.mud);
    }
    hut(ctx,1,shore-2,p);
    for (let i=0;i<2;i++) {
      const x=Math.round(w*(i? .91:.79)), y=shore+3+i*3;
      rect(ctx,x-8,y,17,2,p.roof); rect(ctx,x-6,y+2,13,2,p.beam);
      rect(ctx,x-4,y-3,8,3,p.light);
    }
  }
  function roomBackground(ctx,w,h,room,p,shop) {
    const {left,top,width,height}=room;
    rect(ctx,0,0,w,h,p.night);
    sun(ctx,w*.90,22,p);
    for(let i=0;i<26;i++) rect(ctx,(i*37+6)%w,(i*13+4)%h,2+i%5,1,p.water[i%4]);
    rect(ctx,left-4,top-3,width+8,height+8,p.shadow);
    rect(ctx,left,top,width,height,p.wood);
    for(let i=1;i*5<height;i++) {
      rect(ctx,left,top+i*5,width,1,p.plank);
      for(let x=left+(i%2)*12;x<left+width;x+=24) rect(ctx,x,top+(i-1)*5,1,5,p.plank);
    }
    rect(ctx,left,top,width,2,p.beam);
    rect(ctx,left,top+height-2,width,2,p.beam);
    for(let i=0;i<=6;i++) {
      const x=left+width*i/6;
      rect(ctx,x-1,top-3,3,6,p.beam);
      rect(ctx,x-1,top+height-3,3,6,p.beam);
    }
    if (shop) {
      const x=left+width*.44,y=top+height*.46;
      rect(ctx,x-28,y-4,56,15,p.beam); rect(ctx,x-27,y-5,54,5,p.roof);
      rect(ctx,x-23,y-10,10,5,p.light); rect(ctx,x+13,y-10,9,5,p.foam);
      hut(ctx,x-16,y-14,p);
    }
  }
  function scenery(ctx,w,h,key,paint) {
    if (backgroundKey!==key) {
      art.width=w; art.height=h; backgroundKey=key;
      paint(background);
    }
    ctx.drawImage(art,0,0);
  }
  function label(ctx,x,y,value,p) {
    rect(ctx,x-7,y-6,15,8,p.shadow);
    ctx.fillStyle=p.light;
    ctx.font="bold 6px monospace";
    ctx.textAlign="center";
    ctx.fillText(value,Math.round(x),Math.round(y));
  }
  function person(ctx,x,y,faceLeft,color,p,guest = false,carrying = false,active = false) {
    if (active) rect(ctx,x-6,y-8,12,15,p.light);
    stamp(ctx,guest?GUEST:HERO,{S:guest?"#f1cb7b":"#b75145",H:p.ink,K:guest?p.ink:"#9bdadd",
      E:guest?"#efd0a1":"#fbd4a6",M:color,T:"#ffe7b6",X:"#8a5d3f",P:"#45506a",B:p.ink},x,y,faceLeft);
    if (carrying) {
      rect(ctx,x+3,y,7,1,p.light); rect(ctx,x+4,y+1,5,3,p.roof); rect(ctx,x+5,y+4,3,1,p.shadow);
    }
  }
  function river(ctx,w,h,s,t,contrast) {
    const p=contrast?high:normal, shore=Math.round(h*.30);
    const {x:[,width],d:[,depth]}=s.meta.bounds;
    const sx=x=>9+x*(w-18)/width, sy=d=>shore+d*(h-shore-12)/depth;
    scenery(ctx,w,h,"river:"+w+":"+h+":"+contrast,bg=>riverBackground(bg,w,h,shore,p));
    for(let i=0;i<32;i++) {
      const x=(i*43+Math.floor(t*(i%3+1)/260))%w, y=shore+2+(i*17%Math.max(1,h-shore-5));
      rect(ctx,x,y,3+i%6,1,i<4?p.foam:p.water[(i+1)%4]);
    }
    for(const n of s.nodes||[]) {
      const x=sx(n.pos[0]), y=sy(n.pos[1]);
      rect(ctx,x-4,y,10,2,p.trees);
      if(n.ready) {
        rect(ctx,x-3,y-2,7,2,p.land);
        rect(ctx,x-1,y-5,3,3,FLOWERS[n.kind]||p.light);
        rect(ctx,x,y-4,1,1,p.sun);
      }
    }
    for(const f of s.fish||[]) {
      const [light,body,tail]=FISH_COLORS[f.kind]||FISH_COLORS.ca_linh;
      const y=sy(f.pos[1])+((Math.floor(t/180)+f.id.length)%2);
      stamp(ctx,FISH,{L:light,D:body,T:tail,E:p.ink},sx(f.pos[0]),y,Math.cos(f.heading_deg*Math.PI/180)<0);
    }
    for(const m of s.monsters||[]) {
      const x=sx(m.pos[0]), y=sy(m.pos[1]);
      const alert=m.state==="chase", recoil=m.state==="recoil";
      stamp(ctx,CROCODILE,{D:alert?"#bd5b83":recoil?"#b48b4b":"#56885a",L:alert?"#f7afd0":p.foam,T:p.trees,E:p.light},
        x,y,Boolean(s.player&&m.pos[0]>s.player.pos[0]));
    }
    if (!s.player) return;
    const player=s.player, x=sx(player.pos[0]), y=sy(player.pos[1]);
    const submerged=player.at_surface===false;
    person(ctx,x,submerged?y:y-6,Math.cos(player.heading_deg*Math.PI/180)<0,"#d78966",p,
      false,false,Boolean(player.invuln_ticks&&Math.floor(t/120)%2));
    if(submerged) {
      const kick=Math.floor(t/100)%2;
      rect(ctx,x-2,y+5+kick,2,1,p.light);
      rect(ctx,x+1,y+6-kick,2,1,p.light);
      for(let i=0;i<3;i++) {
        const d=(Math.floor(t/100)+i*6)%20;
        rect(ctx,x-3+i*3,y-8-d,1+(i%2),1,p.foam);
      }
    }
  }
  function room(ctx,w,h,s,t,contrast) {
    const p=contrast?high:normal, shop=s.phase==="shop";
    const b=s.meta.bounds||{x:[0,16],z:[0,10]};
    const width=w-30,height=h-43,left=15,top=21;
    const sx=x=>left+x*width/b.x[1], sy=z=>top+height-z*height/b.z[1];
    scenery(ctx,w,h,"room:"+w+":"+h+":"+contrast+":"+shop,bg=>roomBackground(bg,w,h,{width,height,left,top},p,shop));
    for(let i=0;i<9;i++) {
      const x=left+width*(i+.5)/9,y=top-5+(i%3);
      rect(ctx,x-1,y-2,4,5,Math.floor(t/260+i)%5===0?p.sun:p.light);
      rect(ctx,x-3,y-1,8,1,p.light);
    }
    for(const st of s.stoves||[]) {
      const x=sx(st.pos[0]),y=sy(st.pos[1]),cooking=st.state==="cooking",ready=st.state==="ready";
      rect(ctx,x-9,y-5,19,12,p.beam); rect(ctx,x-8,y-5,17,6,p.shadow);
      rect(ctx,x-6,y-4,13,2,ready?p.foam:p.light);
      rect(ctx,x-4,y-3,9,2,p.ink); rect(ctx,x-3,y-4,7,1,p.light);
      if(cooking) {
        rect(ctx,x-3,y+1,8,2,Math.floor(t/130)%2?p.sun:p.roof);
        for(let i=0;i<3;i++) rect(ctx,x-3+i*3,y-7-(Math.floor(t/190)+i*3)%10,2,1,p.cloud);
        const total=s.meta.menu[st.dish.dish_id].cook_s*s.meta.tick_hz;
        rect(ctx,x-9,y-9,19,2,p.shadow);
        rect(ctx,x-9,y-9,19*(1-st.cook_ticks_left/total),2,p.light);
      }
      if(ready){ rect(ctx,x+7,y-9,1,5,p.foam); rect(ctx,x+5,y-7,5,1,p.foam); }
      label(ctx,x,y+12,st.id,p);
    }
    const customers=new Map((s.customers||[]).map(c=>[c.table_id,c]));
    for(const [i,tb] of (s.tables||[]).entries()) {
      const x=sx(tb.pos[0]),y=sy(tb.pos[1]),c=customers.get(tb.id);
      rect(ctx,x-10,y-4,21,9,p.beam); rect(ctx,x-9,y-5,19,7,p.light);
      rect(ctx,x-5,y-3,11,4,p.roof); rect(ctx,x-3,y-2,7,2,p.cloud);
      if(c) {
        person(ctx,x+8,y-9,i%2===0,COLORS[i%4],p,true);
        if(c.state==="waiting"&&c.patience_ticks_left < s.meta.patience_s*s.meta.tick_hz*.25) {
          rect(ctx,x+12,y-20,3,6,p.light); rect(ctx,x+12,y-12,3,2,p.light);
        }
      }
      label(ctx,x,y+10,tb.id,p);
    }
    if (s.player) person(ctx,sx(s.player.pos[0]),sy(s.player.pos[1]),(s.player.vel?.[0]||0)<0,
      "#d78966",p,false,Boolean(s.hand));
  }
  return { river,room };
})();
