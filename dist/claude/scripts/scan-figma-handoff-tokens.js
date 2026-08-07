// ============================================================
// HANDOFF SCAN v1.3 - PARTE 3/4: tokens de biblioteca
// (tokenOutsideHandoff).
// Executar as 4 partes EM PARALELO, numa unica mensagem.
// Injetar exatamente como esta. Unica area editavel: CONFIG.
// ============================================================
const CONFIG = {
  fileKey: 'FILE_KEY_AQUI',
  allowedLibraries: ['Afya DS - Foundations Global'],
  ignoreLayerNames: ['status-bar', 'keyboard', 'home-indicator'],
  structuralLayers: ['header', 'content', 'footer'],
  iconNameSegments: ['icon', 'icons', 'ico'],
  cap: 8,
  capPerNode: 6,
  vectorClusterThreshold: 5
};
const RULES_VERSION = '1.3';
const enabled = await figma.teamLibrary.getAvailableLibraryVariableCollectionsAsync();
const enabledKeys = new Map(enabled.map(l => [l.key, l.libraryName]));
const page = figma.currentPage;
const IGNORE = new Set(CONFIG.ignoreLayerNames);
const varCache = new Map();
const colCache = new Map();
async function varInfo(id) {
  if (varCache.has(id)) return varCache.get(id);
  let info = null;
  try {
    const v = await figma.variables.getVariableByIdAsync(id);
    if (v) {
      let col = colCache.get(v.variableCollectionId);
      if (col === undefined) { col = await figma.variables.getVariableCollectionByIdAsync(v.variableCollectionId); colCache.set(v.variableCollectionId, col); }
      const libName = col && col.key && enabledKeys.has(col.key) ? enabledKeys.get(col.key) : null;
      info = { name: v.name, colName: col ? col.name : '?', remote: v.remote, key: col ? col.key : null, libName };
    }
  } catch (e) {}
  varCache.set(id, info);
  return info;
}
function boundIdsOf(bv) {
  const ids = [];
  if (!bv) return ids;
  for (const k of Object.keys(bv)) {
    const val = bv[k];
    if (Array.isArray(val)) val.forEach(a => a && a.id && ids.push({ field: k, id: a.id }));
    else if (val && val.id) ids.push({ field: k, id: val.id });
    else if (val && typeof val === 'object') Object.keys(val).forEach(sub => { const a = val[sub]; if (a && a.id) ids.push({ field: k + '.' + sub, id: a.id }); });
  }
  return ids;
}
const mains = page.children.filter(n => n.type === 'FRAME').sort((a, b) => a.name.localeCompare(b.name));
const scopes = [];
for (const main of mains) {
  const counts = {}; const issues = {}; const seenNodes = {};
  function add(cat, loc) {
    counts[cat] = (counts[cat] || 0) + 1;
    if (!issues[cat]) { issues[cat] = { occurrences: 0, affectedNodes: 0, nodesOmitted: 0, truncated: false, locations: [] }; seenNodes[cat] = { order: [], perNode: {} }; }
    const it = issues[cat]; const sn = seenNodes[cat];
    it.occurrences++;
    const key = loc.nodeId || '';
    let idx = sn.order.indexOf(key);
    if (idx === -1) { sn.order.push(key); idx = sn.order.length - 1; it.affectedNodes++; if (idx >= CONFIG.cap) it.nodesOmitted++; }
    sn.perNode[key] = (sn.perNode[key] || 0) + 1;
    if (idx < CONFIG.cap && sn.perNode[key] <= CONFIG.capPerNode) it.locations.push(loc);
    else it.truncated = true;
  }
  const S = { nodeId: main.id, name: main.name, deepLink: 'https://www.figma.com/design/' + CONFIG.fileKey + '?node-id=' + main.id.replace(':', '-'), nodesScanned: 0 };
  const stack = [{ node: main, insideInstance: false, path: '' }];
  while (stack.length) {
    const { node, insideInstance, path } = stack.pop();
    if (node.visible === false) continue;
    const lowerName = node.name.toLowerCase().trim();
    if (IGNORE.has(lowerName)) continue;
    S.nodesScanned++;
    const loc = { layer: path ? path + ' / ' + node.name : node.name, nodeId: node.id, type: node.type };
    if (node.boundVariables) {
      for (const { field, id } of boundIdsOf(node.boundVariables)) {
        const vi = await varInfo(id);
        if (!vi) add('tokenOutsideHandoff', Object.assign({}, loc, { field, token: 'nao resolvido (' + id.slice(0, 40) + ')', reason: 'variavel inacessivel' }));
        else if (vi.remote && !CONFIG.allowedLibraries.includes(vi.libName)) {
          add('tokenOutsideHandoff', Object.assign({}, loc, { field, token: (vi.libName || 'BIBLIOTECA NAO HABILITADA') + ' :: ' + vi.colName + '/' + vi.name, reason: vi.libName ? 'biblioteca fora da allowlist do handoff' : 'colecao remota nao habilitada no arquivo' }));
        }
      }
    }
    if ('children' in node) {
      for (let i = node.children.length - 1; i >= 0; i--) stack.push({ node: node.children[i], insideInstance: insideInstance || node.type === 'INSTANCE', path: loc.layer });
    }
  }
  S.counts = counts; S.issues = issues; scopes.push(S);
}
const agg = {}; const aggNodes = {};
for (const s of scopes) for (const k of Object.keys(s.counts)) { agg[k] = (agg[k] || 0) + s.counts[k]; aggNodes[k] = (aggNodes[k] || 0) + s.issues[k].affectedNodes; }
return { rulesVersion: RULES_VERSION, part: 3, config: CONFIG, fileKey: CONFIG.fileKey, page: { id: page.id, name: page.name }, mainFrames: mains.length, enabledLibraries: Array.from(new Set(enabled.map(l => l.libraryName))).sort(), scopes, aggregate: agg, aggregateAffectedNodes: aggNodes };
