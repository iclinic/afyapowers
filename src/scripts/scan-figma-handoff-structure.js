// ============================================================
// HANDOFF SCAN v1.3 - PARTE 1/4: estrutura, Auto Layout, grid,
// groups, wrappers redundantes e annotations.
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
const pageNames = figma.root.children.map(p => p.name);
const page = figma.currentPage;
const pageIndex = figma.root.children.findIndex(p => p.id === page.id) + 1;
const VECTOR_TYPES = ['VECTOR', 'BOOLEAN_OPERATION', 'LINE', 'STAR', 'POLYGON', 'ELLIPSE'];
const IGNORE = new Set(CONFIG.ignoreLayerNames);
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
  const S = { nodeId: main.id, name: main.name, deepLink: 'https://www.figma.com/design/' + CONFIG.fileKey + '?node-id=' + main.id.replace(':', '-'), nodesScanned: 0, ignoredInvisible: 0, ignoredAsNoise: 0, annotationCount: 0 };
  const childByName = new Map();
  for (const c of main.children) { const k = c.name.toLowerCase().trim(); if (!childByName.has(k)) childByName.set(k, c); }
  if (main.layoutMode === 'NONE') add('missingAutoLayout', { layer: main.name, nodeId: main.id, type: main.type, target: 'frame principal', layoutMode: 'NONE' });
  for (const req of CONFIG.structuralLayers) {
    const sn = childByName.get(req);
    if (!sn) { add('missingStructureLayer', { missing: req, nodeId: main.id }); continue; }
    const lm = ('layoutMode' in sn) ? sn.layoutMode : 'n/a';
    if (lm === 'NONE' || lm === 'n/a') add('missingAutoLayout', { layer: main.name + ' / ' + sn.name, nodeId: sn.id, type: sn.type, target: req, layoutMode: lm });
  }
  const stack = [{ node: main, insideInstance: false, path: '', clusterRoot: null }];
  while (stack.length) {
    const { node, insideInstance, path, clusterRoot } = stack.pop();
    if (node.visible === false) { S.ignoredInvisible++; continue; }
    const lowerName = node.name.toLowerCase().trim();
    if (IGNORE.has(lowerName)) { S.ignoredAsNoise++; continue; }
    S.nodesScanned++;
    const loc = { layer: path ? path + ' / ' + node.name : node.name, nodeId: node.id, type: node.type };
    try { if (node.annotations && node.annotations.length > 0) S.annotationCount += node.annotations.length; } catch (e) {}
    if ('layoutMode' in node && node.layoutMode === 'GRID') add('gridAutoLayout', Object.assign({}, loc, { resolveIn: insideInstance ? 'componente de origem na biblioteca' : 'aqui' }));
    if (!insideInstance) {
      if (node.type === 'GROUP' && !clusterRoot) add('groupNode', loc);
      const isStructural = CONFIG.structuralLayers.includes(lowerName);
      if (node.type === 'FRAME' && node.children && node.children.length === 1 && node.id !== main.id && !isStructural) {
        const only = node.children[0];
        const noVisual = (!Array.isArray(node.fills) || !node.fills.some(f => f.visible !== false)) && (!Array.isArray(node.strokes) || node.strokes.length === 0) && (!node.effects || node.effects.length === 0);
        const noPad = ['paddingLeft', 'paddingRight', 'paddingTop', 'paddingBottom'].every(p => !node[p]);
        if ((only.type === 'FRAME' || only.type === 'GROUP' || only.type === 'INSTANCE') && noVisual && noPad) add('redundantWrapper', Object.assign({}, loc, { onlyChild: only.name }));
      }
    }
    if ('children' in node) {
      const childHasVectors = node.children.some(c => VECTOR_TYPES.includes(c.type) || c.type === 'GROUP');
      const nextClusterRoot = clusterRoot || (childHasVectors && node.type === 'FRAME' ? { id: node.id, name: node.name, layer: loc.layer } : null);
      for (let i = node.children.length - 1; i >= 0; i--) stack.push({ node: node.children[i], insideInstance: insideInstance || node.type === 'INSTANCE', path: loc.layer, clusterRoot: nextClusterRoot });
    }
  }
  if (S.annotationCount === 0) add('missingAnnotations', { nodeId: main.id, note: 'nenhuma annotation no frame ou descendentes' });
  S.counts = counts; S.issues = issues; scopes.push(S);
}
const agg = {}; const aggNodes = {};
for (const s of scopes) for (const k of Object.keys(s.counts)) { agg[k] = (agg[k] || 0) + s.counts[k]; aggNodes[k] = (aggNodes[k] || 0) + s.issues[k].affectedNodes; }
return { rulesVersion: RULES_VERSION, part: 1, config: CONFIG, fileKey: CONFIG.fileKey, page: { id: page.id, name: page.name }, pagesInFile: pageNames.length, pageIndex, pageNames, mainFrames: mains.length, scopes, aggregate: agg, aggregateAffectedNodes: aggNodes };
