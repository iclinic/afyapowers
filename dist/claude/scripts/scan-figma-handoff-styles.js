// ============================================================
// HANDOFF SCAN v1.3 - PARTE 4/4: espacamento, cor, ilustracao
// e tipografia.
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
const RULES_VERSION = '1.4';
const page = figma.currentPage;
const VECTOR_TYPES = ['VECTOR', 'BOOLEAN_OPERATION', 'LINE', 'STAR', 'POLYGON', 'ELLIPSE'];
const PADDING_SIDES = [['paddingTop', 'top'], ['paddingRight', 'right'], ['paddingBottom', 'bottom'], ['paddingLeft', 'left']];
const IGNORE = new Set(CONFIG.ignoreLayerNames);
const styleCache = new Map();
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
  const vectorClusters = new Map();
  const stack = [{ node: main, insideInstance: false, path: '', clusterRoot: null }];
  while (stack.length) {
    const { node, insideInstance, path, clusterRoot } = stack.pop();
    if (node.visible === false) continue;
    const lowerName = node.name.toLowerCase().trim();
    if (IGNORE.has(lowerName)) continue;
    S.nodesScanned++;
    const loc = { layer: path ? path + ' / ' + node.name : node.name, nodeId: node.id, type: node.type };
    const isVector = VECTOR_TYPES.includes(node.type);
    // Espacamento conta um achado por camada e por tipo: um para gap, um para
    // padding com todos os lados afetados agrupados. Contar cada lado como um
    // achado separado inflava o total e distorcia a priorizacao.
    if ('layoutMode' in node && node.layoutMode !== 'NONE' && node.type !== 'INSTANCE' && !insideInstance) {
      const bv = node.boundVariables || {};
      if (typeof node.itemSpacing === 'number' && node.itemSpacing > 0 && !bv.itemSpacing) add('hardcodedGapOrPadding', Object.assign({}, loc, { prop: 'gap', value: node.itemSpacing }));
      const sides = [];
      for (const [p, side] of PADDING_SIDES) {
        if (typeof node[p] === 'number' && node[p] > 0 && !bv[p]) sides.push({ side, value: node[p] });
      }
      if (sides.length) add('hardcodedGapOrPadding', Object.assign({}, loc, { prop: 'padding', sides }));
    }
    if (!insideInstance && node.type !== 'INSTANCE' && 'fills' in node && Array.isArray(node.fills)) {
      const bvFills = node.boundVariables && node.boundVariables.fills;
      const hasStyle = 'fillStyleId' in node && node.fillStyleId && node.fillStyleId !== figma.mixed;
      const solid = node.fills.find(f => f.visible !== false && f.type === 'SOLID');
      if (solid && !hasStyle && !(solid.boundVariables && solid.boundVariables.color) && !bvFills) {
        if (isVector && clusterRoot) {
          const c = vectorClusters.get(clusterRoot.id) || { root: clusterRoot, vectorCount: 0 };
          c.vectorCount++;
          vectorClusters.set(clusterRoot.id, c);
        } else {
          add('hardcodedFillColor', Object.assign({}, loc, { value: 'rgb(' + Math.round(solid.color.r * 255) + ',' + Math.round(solid.color.g * 255) + ',' + Math.round(solid.color.b * 255) + ')' }));
        }
      }
    }
    if (node.type === 'TEXT' && !insideInstance) {
      const sid = node.textStyleId;
      if (sid && sid !== figma.mixed && sid !== '') {
        let st = styleCache.get(sid);
        if (st === undefined) { st = await figma.getStyleByIdAsync(sid); styleCache.set(sid, st); }
        if (st && !st.remote) add('usingLocalTextStyle', Object.assign({}, loc, { style: st.name }));
      } else {
        const bv = node.boundVariables || {};
        const hasTypoToken = bv.fontSize || bv.fontFamily || bv.fontStyle || bv.lineHeight || bv.fontWeight;
        const fs = node.fontSize === figma.mixed ? 'mixed' : node.fontSize;
        const fn = node.fontName === figma.mixed ? { family: 'mixed', style: '' } : node.fontName;
        const cur = fn.family + ' ' + fn.style + ' ' + fs;
        if (hasTypoToken) add('withoutTextStyle', Object.assign({}, loc, { text: node.characters.slice(0, 40), current: cur }));
        else add('withoutTypographyToken', Object.assign({}, loc, { text: node.characters.slice(0, 40), current: cur }));
      }
    }
    if ('children' in node) {
      const childHasVectors = node.children.some(c => VECTOR_TYPES.includes(c.type) || c.type === 'GROUP');
      const nextClusterRoot = clusterRoot || (childHasVectors && node.type === 'FRAME' ? { id: node.id, name: node.name, layer: loc.layer } : null);
      for (let i = node.children.length - 1; i >= 0; i--) stack.push({ node: node.children[i], insideInstance: insideInstance || node.type === 'INSTANCE', path: loc.layer, clusterRoot: nextClusterRoot });
    }
  }
  for (const [, c] of Array.from(vectorClusters.entries()).sort((a, b) => a[0].localeCompare(b[0]))) {
    if (c.vectorCount >= CONFIG.vectorClusterThreshold) add('illustrationVectorCluster', { layer: c.root.layer, nodeId: c.root.id, vectorsWithHardcodedFill: c.vectorCount, fix: 'converter em asset exportavel ou componente de ilustracao' });
    else if (c.vectorCount > 0) add('hardcodedFillColor', { layer: c.root.layer, nodeId: c.root.id, note: c.vectorCount + ' vetor(es) com fill hardcoded no subtree' });
  }
  S.counts = counts; S.issues = issues; scopes.push(S);
}
const agg = {}; const aggNodes = {};
for (const s of scopes) for (const k of Object.keys(s.counts)) { agg[k] = (agg[k] || 0) + s.counts[k]; aggNodes[k] = (aggNodes[k] || 0) + s.issues[k].affectedNodes; }
return { rulesVersion: RULES_VERSION, part: 4, config: CONFIG, fileKey: CONFIG.fileKey, page: { id: page.id, name: page.name }, mainFrames: mains.length, scopes, aggregate: agg, aggregateAffectedNodes: aggNodes };
