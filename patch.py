"""Apply or restore the Claudian cross-project messaging patch. Requires Python 3 and Node.js."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


CHANGES = [
    ('Xz={includeProviders:', 'Xz={includeProjects:{type:"boolean",description:"Return available destination Projects as {id, name} for starting a new session."},includeProviders:'),
    ('Yz={sessionId:', 'Yz={projectId:{type:"string",description:"Destination Project ID for a new session. Use claudian_list_destinations with includeProjects: true to look it up. Omit to inherit the calling Project. Only valid without sessionId."},sessionId:'),
    ('Returns {sessions, truncated?, providers?}.', 'Returns {sessions, truncated?, providers?, projects?}. Set includeProjects to list destination Project IDs and names.'),
    ('if(n===ki){let d=i.includeProviders', 'if(n===ki){if(i.includeProjects!==void 0&&typeof i.includeProjects!=="boolean")return{ok:!1,error:"includeProjects must be a boolean."};let d=i.includeProviders'),
    ('includeProviders:d,limit:c,...u?', 'includeProviders:d,limit:c,...i.includeProjects?{includeProjects:true}:{},...u?'),
    ('for(let d of["sessionId","text","provider","model","reasoning"])', 'for(let d of["sessionId","text","provider","model","reasoning","projectId"])'),
    ('if(s!=="queue"){if(a.sessionId===void 0)', 'if(a.projectId!==void 0&&a.sessionId!==void 0)return{ok:!1,error:"projectId applies only to new sessions."};if(s!=="queue"){if(a.sessionId===void 0)'),
    ('...t.includeProviders?{providers:e_e(o.getCommittedSettings())}', '...t.includeProjects?{projects:o.projects.list().filter(p=>!p.isArchived).map(p=>({id:p.id,name:p.name}))}:{},...t.includeProviders?{providers:e_e(o.getCommittedSettings())}'),
    ('let g=await o.createConversation({providerId:m.providerId,selectedModel:m.model,...r.projectId?{projectId:r.projectId}:{},origin:{kind:"session-tool"', 'const destination=t.projectId??r.projectId;if(t.projectId){const p=o.projects.get(destination);if(!p||p.isArchived)throw new Error("Destination Project is unavailable. List available Projects with includeProjects: true.")}let g=await o.createConversation({providerId:m.providerId,selectedModel:m.model,...destination?{projectId:destination}:{},origin:{kind:"session-tool"'),
    (r'Sessions you start with \`claudian_send_message\` join this project.', r'Sessions you start with \`claudian_send_message\` join this project by default. To start in another Project, look up its ID with \`claudian_list_destinations\` (includeProjects: true), then pass projectId when sending the first message.'),
]


def transform(data, reverse=False):
    for old, new in CHANGES:
        source, target = (new, old) if reverse else (old, new)
        if data.count(source.encode()) != 1:
            raise SystemExit('Unrecognized bundle or partial patch. No files changed.')
        data = data.replace(source.encode(), target.encode(), 1)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plugin-dir', type=Path, required=True, help='Installed realclaudian directory containing manifest.json and main.js')
    parser.add_argument('--restore', action='store_true', help='Restore the original matching bundle')
    args = parser.parse_args()
    plugin = args.plugin_dir.resolve()
    manifest = json.loads((plugin / 'manifest.json').read_text(encoding='utf-8-sig'))
    if manifest.get('id') != 'realclaudian':
        raise SystemExit('Please select the realclaudian plugin directory.')
    if manifest.get('version') != '2.3.47':
        raise SystemExit('This release supports Claudian 2.3.47 only.')
    bundle = plugin / 'main.js'
    current = bundle.read_bytes()
    patched = all(current.count(new.encode()) == 1 for _, new in CHANGES)
    original = transform(current, reverse=True) if patched else current
    if hashlib.sha256(original).hexdigest() != '9949fe83d13e996999b615851c113a764e1b3a019d256c9609b5562b26ee3a68':
        raise SystemExit('Unrecognized original bundle. No files changed.')
    updated = transform(original)
    if patched and updated != current:
        raise SystemExit('Unexpected patched bundle. No files changed.')
    desired = original if args.restore else updated
    if desired == current:
        print('Already restored.' if args.restore else 'Already patched.')
        return
    digest = hashlib.sha256(original).hexdigest()
    backup = plugin / ('main.js.' + digest + '.bak')
    if args.restore and not backup.exists():
        raise SystemExit('Matching original backup is missing.')
    if backup.exists() and backup.read_bytes() != original:
        raise SystemExit('Backup differs from expected original. No files changed.')
    with tempfile.NamedTemporaryFile(dir=plugin, suffix='.js', delete=False) as temp:
        temporary = Path(temp.name)
        temp.write(desired)
    try:
        subprocess.run(['node', '--check', str(temporary)], check=True)
        if not backup.exists():
            with backup.open('xb') as output:
                output.write(original)
        if bundle.read_bytes() != current:
            raise SystemExit('Installed bundle changed during patching. Retry.')
        os.replace(temporary, bundle)
    finally:
        temporary.unlink(missing_ok=True)
    print(('Restored' if args.restore else 'Patched'), 'Claudian', manifest['version'])


if __name__ == '__main__':
    main()
