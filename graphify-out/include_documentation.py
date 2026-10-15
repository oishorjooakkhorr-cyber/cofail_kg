"""Rebuild the documentation fragment and merge without changing existing AST data."""
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'graphify-out'
graph = json.loads((OUT / 'graph.json').read_text(encoding='utf-8'))
# The Markdown extractor can mistake label lists for links to nonexistent files.
input_ids = {n['id'] for n in graph['nodes']}
invalid_links = [e for e in graph['links'] if e['source'] not in input_ids or e['target'] not in input_ids]
graph['links'] = [e for e in graph['links'] if e['source'] in input_ids and e['target'] in input_ids]
previous_path=OUT/'documentation-extraction.json'
if previous_path.exists():
    previous=json.loads(previous_path.read_text(encoding='utf-8'))
    previous_ids={n['id'] for n in previous['nodes']}
    previous_edges={(e['source'],e['target'],e.get('relation'),e.get('source_file'),e.get('source_location')) for e in previous['edges']}
    graph['nodes']=[n for n in graph['nodes'] if n['id'] not in previous_ids or n.get('_origin') == 'ast']
    # Clustering can reorient or merge document links; remove their old endpoints too.
    graph['links']=[e for e in graph['links'] if e['source'] not in previous_ids
                    and e['target'] not in previous_ids
                    and (e['source'],e['target'],e.get('relation'),e.get('source_file'),e.get('source_location')) not in previous_edges]
original_nodes = list(graph['nodes'])
original_edges = list(graph['links'])
nodes, edges = {}, {}
documents = (['README.md', 'CLAUDE.md']
             + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'docs').glob('*.md'))
             + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'data/processed').glob('*.md'))
             + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'data/processed/manifests').glob('*.md'))
             + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'results/diagnostics').rglob('*.md'))
             + sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'results/semantics').rglob('*.md')))
def slug(s):
    return re.sub('[^a-z0-9]+', '_', s.lower()).strip('_')
def stem(p):
    return slug(str(Path(p).with_suffix('')).replace('\\', '/'))
def node(p, label, line, kind='concept', entity=None, **extra):
    ident = stem(p) + '_' + slug(entity or label)
    if kind == 'document':
        ident = next((n['id'] for n in original_nodes if n.get('source_file') == p
                      and n.get('file_type') == 'document' and n.get('label') == label), stem(p))
    nodes[ident] = dict(id=ident, label=label, file_type=kind, source_file=p,
                        source_location=f'L{line}', _origin='semantic', **extra)
    return ident
def edge(a,b,rel,p,line,confidence='EXTRACTED',score=1.0,**extra):
    if a == b: return
    key=(a,b,rel,p,line)
    edges[key]=dict(source=a,target=b,relation=rel,confidence=confidence,
                    confidence_score=score,weight=1.0,source_file=p,
                    source_location=f'L{line}',_origin='semantic',**extra)

texts = {p:(ROOT/p).read_text(encoding='utf-8-sig').splitlines() for p in documents}
doc_ids={p:node(p, re.sub(r'^#+\s*','',texts[p][0]),1,'document',entity='document') for p in documents}
sections={}
owners={}
for p,lines in texts.items():
    stack=[]; owners[p]={}; sections[p]=[]
    for ln,text in enumerate(lines,1):
        m=re.match(r'^(#{1,4})\s+(.+)',text)
        if m and ln != 1:
            level=len(m[1]); title=re.sub(r'[`*]','',m[2])
            ident=node(p,title,ln,'concept',entity=title)
            while stack and stack[-1][0]>=level: stack.pop()
            parent=stack[-1][1] if stack else doc_ids[p]
            edge(parent,ident,'references',p,ln,context='Document section hierarchy')
            stack.append((level,ident)); sections[p].append((title,ident,ln))
        owners[p][ln]=stack[-1][1] if stack else doc_ids[p]
    for idx,(title,ident,start) in enumerate(sections[p]):
        end=sections[p][idx+1][2]-1 if idx+1<len(sections[p]) else len(lines)
        body='\n'.join(lines[start:end]).strip()
        nodes[ident]['summary']=re.sub(r'\s+',' ',body)[:650]
        nodes[ident]['source_end_line']=end
        status=re.search(r'\[(FROZEN|PROVISIONAL|TBD@S\d+|DEFAULT)\]',title)
        if status: nodes[ident]['status']=status[1]
        why=re.search(r'(?m)^Why:\s*(.+)',body)
        if why: nodes[ident]['rationale']=why[1]

protocol='docs/frozen_pilot_protocol.md'
protocol_sections={re.match(r'^(\d+)\.\s',t)[1]:ident for t,ident,_ in sections[protocol] if re.match(r'^\d+\.\s',t)}
# Section titles such as "14.1 Label B" omit the trailing dot.
for t,ident,_ in sections[protocol]:
    m=re.match(r'^(\d+\.\d+)\s',t)
    if m: protocol_sections[m[1]]=ident
stage_ids={re.match(r'^(S\d+)\s',t)[1]:ident for t,ident,_ in sections['docs/pipeline_runbook.md'] if re.match(r'^S\d+\s',t)}
gate_ids={re.match(r'^(D\d+)\s',t)[1]:ident for t,ident,_ in sections['docs/decision_rules.md'] if re.match(r'^D\d+\s',t)}

code_by_file={}
for n in original_nodes:
    if n.get('file_type')=='code': code_by_file.setdefault(n.get('source_file','').replace('\\','/'),[]).append(n)
for p,lines in texts.items():
    for ln,text in enumerate(lines,1):
        owner=owners[p][ln]
        for target,did in doc_ids.items():
            if target != p and (target in text or ('`'+Path(target).name+'`') in text):
                edge(owner,did,'references',p,ln,context='Explicit document reference')
        for m in re.finditer(r'§\s*(\d+(?:\.\d+)?)',text):
            target=protocol_sections.get(m[1])
            if target: edge(owner,target,'references',p,ln,context='Explicit protocol section reference')
        for gate,gid in gate_ids.items():
            if re.search(r'\b'+gate+r'\b',text): edge(owner,gid,'references',p,ln,context='Explicit gate reference')
        for cp,cnodes in code_by_file.items():
            if cp and cp in text:
                # Prefer public entry points; connect directly to actual AST symbols.
                selected=[n for n in cnodes if n['label'].lower().rstrip('()') in ('main','load_raw_records','read_metadata','analyze','write_once','read_frozen_hashes')]
                if not selected: selected=cnodes[:1]
                for cn in selected: edge(owner,cn['id'],'references',p,ln,context='Documentation names the implemented source file')

# Named design entities: definitions stay attached to their owning protocol sections.
concepts=[('BioHopR','3.1','BioHopR'),('PrimeKG','3.2','PrimeKG'),('Frozen hashes','3.4','frozen_hashes.yaml'),
('Query grouping','0.4','query grouping'),('Accepted relation sets R1 and R2','4','R1'),('Valid bridges B_q','6','B_q'),
('Question-valid answer set T_q','6','T_q'),('CONSISTENT query','7.1','CONSISTENT'),('LEAKY_QUESTION exclusion','7.1','LEAKY_QUESTION'),
('Primary population','7.2','primary population'),('Deterministic stratified sampling','8','stratified'),
('Agent independence','9.2','independen'),('Agent-input isolation','9.3','agent-input'),('Episode status','9.5','episode status'),
('inspect_entity tool','10','inspect_entity'),('get_neighbors tool','10','get_neighbors'),('Trace graph TG_i','11','trace graph'),
('Exact name and ID normalization','12','normalization'),('Label A answer status','13','Label A'),('Label B path status','14.1','Label B'),
('Hop-1 status','14.3','hop-1 status'),('Answer co-failure CF3 and CF4','16.1','CF3'),('Path co-failure','16.3','PCF_'),
('Pairwise error agreement','16.4','error agreement'),('Within-query chance baselines','17','chance baseline'),
('Checkpoint and resume','19','resume'),('Phase 2 intervention design','21','intervention'),('Change control','20','change control')]
for label,sec,term in concepts:
    definition=protocol_sections.get(sec)
    if not definition: continue
    line=int(nodes[definition]['source_location'][1:])
    cid=node(protocol,label,line,'rationale',entity='concept_'+label)
    edge(definition,cid,'references',protocol,line,context='Named design concept defined in this section')
    # Cross-document explicit mentions, one edge per containing section.
    seen=set()
    for p,lines in texts.items():
        if p==protocol: continue
        for ln,text in enumerate(lines,1):
            owner=owners[p][ln]
            if term.casefold() in text.casefold() and owner not in seen:
                edge(owner,cid,'references',p,ln,context='Explicit mention of the named design concept'); seen.add(owner)

# Preserve paper details and verification state exactly as documented; no external validation implied.
p='docs/provenance.md'
for ln,text in enumerate(texts[p],1):
    if not text.startswith('|'): continue
    cols=[s.strip() for s in text.strip('|').split('|')]
    if len(cols)==6 and cols[0] not in ('Stage','---'):
        component,source,status=cols[1],cols[3],cols[5]
        if source in ('—','---'): continue
        cid=node(p,component,ln,'concept',entity='component_'+component,provenance_type=cols[4])
        edge(owners[p][ln],cid,'references',p,ln)
        kind='paper' if re.search(r'\(20\d\d\)|arXiv',source) else 'concept'
        sid=node(p,source,ln,kind,entity='source_'+source,citation_status=status)
        edge(cid,sid,'cites',p,ln,context='Provenance attribution; verification state copied from source')
        for stage in re.findall(r'S\d+',cols[0]):
            if stage in stage_ids: edge(stage_ids[stage],cid,'references',p,ln)

# Link source docstrings' scientific citations back to the authoritative definitions.
for cp,cnodes in code_by_file.items():
    file=ROOT/cp
    if not file.is_file(): continue
    lines=file.read_text(encoding='utf-8-sig').splitlines()
    for ln,text in enumerate(lines,1):
        for sec in re.findall(r'§\s*(\d+(?:\.\d+)?)',text):
            if sec not in protocol_sections: continue
            preceding=[n for n in cnodes if int(n.get('source_location','L1').split(':')[0].lstrip('L'))<=ln]
            if preceding:
                cn=max(preceding,key=lambda n:int(n.get('source_location','L1').split(':')[0].lstrip('L')))
                edge(cn['id'],protocol_sections[sec],'references',cp,ln,context='Code explicitly cites protocol section')

fragment=dict(nodes=list(nodes.values()),edges=list(edges.values()),hyperedges=[],input_tokens=0,output_tokens=0,
              extraction_metadata=dict(documents=documents,method='Document sections, explicit cross-references, named design concepts and provenance attributions; code references use existing AST IDs',
                                       rejected_input_links=invalid_links))
existing={n['id'] for n in graph['nodes']}
graph['nodes'].extend(n for ident,n in nodes.items() if ident not in existing)
keys={(e['source'],e['target'],e.get('relation'),e.get('source_file'),e.get('source_location')) for e in graph['links']}
graph['links'].extend(e for e in edges.values() if (e['source'],e['target'],e['relation'],e['source_file'],e['source_location']) not in keys)
ids={n['id'] for n in graph['nodes']}
assert len(ids)==len(graph['nodes'])
assert all(e['source'] in ids and e['target'] in ids for e in graph['links'])
assert all(n in graph['nodes'] for n in original_nodes)
assert all(e in graph['links'] for e in original_edges)
assert all(re.fullmatch('[a-z0-9_]+',n['id']) for n in nodes.values())
(OUT/'documentation-extraction.json').write_text(json.dumps(fragment,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'graph.json').write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Rejected {len(invalid_links)} input links with missing endpoints; full records saved in extraction_metadata.rejected_input_links.')
print(json.dumps(dict(document_count=len(documents),added_nodes=len(nodes),added_edges=len(edges),total_nodes=len(graph['nodes']),total_edges=len(graph['links']),types=dict(Counter(n['file_type'] for n in nodes.values())),doc_code_edges=sum(e['source'] not in nodes or e['target'] not in nodes for e in edges.values()),coverage={p:sum(n['source_file']==p for n in nodes.values()) for p in documents}),indent=2))
