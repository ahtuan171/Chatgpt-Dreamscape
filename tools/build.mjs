import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(repo,p),'utf8');
const b64=p=>fs.readFileSync(path.join(repo,p)).toString('base64');
const manifest=JSON.parse(read('assets/wallpapers/manifest.json'));
const petManifest=JSON.parse(read('assets/pets/victor/manifest.json'));
const wallpapers=manifest.map(w=>({id:w.id,name:w.name,dim:w.dim,group:w.group,appearance:w.appearance||'dark',uri:'data:image/webp;base64,'+b64(w.file)}));
const victor=Object.fromEntries(Object.entries(petManifest).map(([kind,frames])=>[kind,frames.map(file=>'data:image/webp;base64,'+b64(file))]));
const css=read('src/theme.css');
const chunks=['storage','theme','pet','adapter','ui','main'].map(name=>read(`src/${name}.js`));
const header=`// ==UserScript==
// @name         ChatGPT Dreamscape
// @namespace    https://github.com/ahtuan171/Chatgpt-Dreamscape
// @version      0.3.12
// @description  Personal wallpapers and Victor the gray pixel companion for ChatGPT desktop.
// @match        https://chatgpt.com/*
// @run-at       document-idle
// @grant        none
// @noframes
// @downloadURL  https://raw.githubusercontent.com/ahtuan171/Chatgpt-Dreamscape/main/dist/dreamscape.user.js
// @updateURL    https://raw.githubusercontent.com/ahtuan171/Chatgpt-Dreamscape/main/dist/dreamscape.user.js
// ==/UserScript==
`;
const output=header+'\n(()=>{\n"use strict";\n'+
  'const ASSETS='+JSON.stringify({wallpapers,victor})+';\n'+
  'const STYLES='+JSON.stringify(css)+';\n'+chunks.join('\n')+'\n})();\n';
fs.mkdirSync(path.join(repo,'dist'),{recursive:true});
fs.writeFileSync(path.join(repo,'dist/dreamscape.user.js'),output);
console.log(`Built dist/dreamscape.user.js (${Math.round(Buffer.byteLength(output)/1024)} KiB), ${wallpapers.length} wallpapers, ${Object.values(victor).flat().length} Victor frames`);
