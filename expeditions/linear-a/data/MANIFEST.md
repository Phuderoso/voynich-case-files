# Linear A data manifest
- `LinearAInscriptions.js` from [mwenge/lineara.xyz](https://github.com/mwenge/lineara.xyz) at commit `9c81beb`,
  sha256 `9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e`, 1 609 512 bytes, 1 721 documents.
  Fetch: `curl -sL -o LinearAInscriptions.js https://raw.githubusercontent.com/mwenge/lineara.xyz/9c81beb/LinearAInscriptions.js`.
  Not copied here (the repository declares no licence). Convert to `ins.json` with Node:
  `node -e 'const fs=require("fs");eval(fs.readFileSync("LinearAInscriptions.js","utf8")+";global.I=inscriptions;");const o={};for(const [k,v] of I)o[k]=v;fs.writeFileSync("ins.json",JSON.stringify(o))'`
  Run tools from the folder holding `ins.json`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
