// ============================================================
// HANDOFF SCAN v1.3 - PARTE 2/4: nomenclatura de camadas
// (namingViolation e defaultLayerName).
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
const KEBAB = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const PASCAL_KEBAB = /^[A-Z][A-Za-z0-9]*(-[a-z0-9]+)*$/;
const KEBAB_PATH = /^[a-z0-9]+(-[a-z0-9]+)*(\/[a-z0-9]+(-[a-z0-9]+)*)+$/;
const FIGMA_DEFAULT = /^(Frame|Group|Rectangle|Ellipse|Line|Arrow|Vector|Polygon|Star|Text|Component|Component Set|Instance|Section|Slice|Union|Subtract|Intersect|Exclude|Mask|Image|Layer|Clip path group)(\s+\d+)?$/;
const FIGMA_VARIANT_DEFAULT = /^Property\s+\d+=/;
const SVG_ARTIFACT = /^(path|g|svg|use|defs|rect|circle|polyline|clip-?path|clippath|shape|oval|bitmap|combined shape)(\s*\d+)?$/;
const FILE_NAME = /\.(png|jpe?g|svg|gif|webp|pdf)$/i;
const NON_ENGLISH = /[àáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ]/;
const VECTOR_TYPES = ['VECTOR', 'BOOLEAN_OPERATION', 'LINE', 'STAR', 'POLYGON', 'ELLIPSE'];
const IGNORE = new Set(CONFIG.ignoreLayerNames);
function defaultNameReason(nm) {
  if (FIGMA_DEFAULT.test(nm)) return 'nome automatico do Figma';
  if (FIGMA_VARIANT_DEFAULT.test(nm)) return 'variante sem propriedade renomeada';
  if (SVG_ARTIFACT.test(nm)) return 'artefato de import (SVG/AI/Sketch)';
  if (FILE_NAME.test(nm)) return 'nome de arquivo importado';
  return null;
}
function hasIconSegment(nm) { return nm.toLowerCase().split('/').some(seg => CONFIG.iconNameSegments.includes(seg.trim())); }
const libAssetCache = new Map();
async function isLibraryAsset(node) {
  const nm = node.name;
  if (libAssetCache.has(nm)) return libAssetCache.get(nm);
  let remote = false;
  try { const mc = await node.getMainComponentAsync(); remote = !!(mc && mc.remote); } catch (e) {}
  libAssetCache.set(nm, remote);
  return remote;
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
  const stack = [{ node: main, insideInstance: false, path: '', clusterRoot: null }];
  while (stack.length) {
    const { node, insideInstance, path, clusterRoot } = stack.pop();
    if (node.visible === false) continue;
    const lowerName = node.name.toLowerCase().trim();
    if (IGNORE.has(lowerName)) continue;
    S.nodesScanned++;
    const loc = { layer: path ? path + ' / ' + node.name : node.name, nodeId: node.id, type: node.type };
    const isVector = VECTOR_TYPES.includes(node.type);
    // Primitivas de desenho dentro de um subtree vetorial (vetores e groups) ficam
    // de fora da regra de nome: a correcao desse subtree e converter em asset, entao
    // os nomes internos nao sao superficie de handoff. A raiz do cluster continua
    // sendo verificada, porque e uma camada nomeada pelo designer da tela.
    const insideDrawing = (isVector || node.type === 'GROUP') && clusterRoot;
    if (!insideInstance && node.id !== main.id && !insideDrawing) {
      const nm = node.name;
      const iconish = node.type === 'INSTANCE' && (KEBAB_PATH.test(nm) || hasIconSegment(nm));
      const isLibIcon = iconish && await isLibraryAsset(node);
      if (!isLibIcon) {
        const dflt = defaultNameReason(nm);
        if (dflt) add('defaultLayerName', Object.assign({}, loc, { name: nm, reason: dflt }));
        else {
          let viol = null; let extra = null;
          // Texto cujo nome repete o conteudo tem prioridade sobre a checagem de
          // ingles: a correcao semantica ja resolve o nome inteiro, enquanto
          // "renomear em ingles" produziria um nome traduzido e ainda errado.
          const isContentName = node.type === 'TEXT' && nm === node.characters && !(KEBAB.test(nm) && nm.split('-').length <= 3);
          if (isContentName) { viol = 'texto sem nome semantico (nome = conteudo)'; if (NON_ENGLISH.test(nm)) extra = 'o nome tambem esta fora do ingles'; }
          else if (NON_ENGLISH.test(nm)) viol = 'nome fora do ingles';
          else if (node.type === 'INSTANCE' || node.type === 'COMPONENT' || node.type === 'COMPONENT_SET') { if (!PASCAL_KEBAB.test(nm)) viol = 'componente fora de PascalCase(-kebab)'; }
          else if (!KEBAB.test(nm)) viol = 'layer fora de kebab-case';
          if (viol) {
            const l = Object.assign({}, loc, { violation: viol });
            if (extra) l.note = extra;
            add('namingViolation', l);
          }
        }
      }
    }
    if ('children' in node) {
      const childHasVectors = node.children.some(c => VECTOR_TYPES.includes(c.type) || c.type === 'GROUP');
      const nextClusterRoot = clusterRoot || (childHasVectors && node.type === 'FRAME' ? { id: node.id, name: node.name, layer: loc.layer } : null);
      for (let i = node.children.length - 1; i >= 0; i--) stack.push({ node: node.children[i], insideInstance: insideInstance || node.type === 'INSTANCE', path: loc.layer, clusterRoot: nextClusterRoot });
    }
  }
  S.counts = counts; S.issues = issues; scopes.push(S);
}
const agg = {}; const aggNodes = {};
for (const s of scopes) for (const k of Object.keys(s.counts)) { agg[k] = (agg[k] || 0) + s.counts[k]; aggNodes[k] = (aggNodes[k] || 0) + s.issues[k].affectedNodes; }
return { rulesVersion: RULES_VERSION, part: 2, config: CONFIG, fileKey: CONFIG.fileKey, page: { id: page.id, name: page.name }, mainFrames: mains.length, scopes, aggregate: agg, aggregateAffectedNodes: aggNodes };
