"""Download 30 Markdown docs from kubernetes/website (CC BY 4.0) and write data/manifest.json."""
import json, re, sys, urllib.request
from config import ROOT

RAW = 'https://raw.githubusercontent.com/kubernetes/website/main/content/en/docs/'
GH = 'https://github.com/kubernetes/website/blob/main/content/en/docs/'
SITE = 'https://kubernetes.io/docs/'
BASE = 'concepts/'
SELECTION = {
    'APP_ENG': ['workloads/controllers/deployment.md', 'workloads/controllers/replicaset.md',
                'workloads/controllers/statefulset.md', 'workloads/controllers/daemonset.md',
                'workloads/controllers/job.md', 'workloads/controllers/cron-jobs.md',
                'workloads/pods/_index.md', 'workloads/pods/pod-lifecycle.md',
                'workloads/pods/init-containers.md', 'workloads/autoscaling.md'],
    'PLATFORM_ENG': ['storage/volumes.md', 'storage/persistent-volumes.md', 'storage/storage-classes.md',
                     'storage/dynamic-provisioning.md', 'storage/volume-snapshots.md',
                     'storage/ephemeral-volumes.md', 'storage/projected-volumes.md',
                     'storage/storage-capacity.md', 'storage/volume-snapshot-classes.md',
                     'storage/volume-pvc-datasource.md'],
    'SECURITY_ENG': ['security/rbac-good-practices.md', 'security/service-accounts.md',
                     'security/pod-security-standards.md', 'security/secrets-good-practices.md',
                     'security/multi-tenancy.md'],
    'ALL_EMPLOYEES': ['overview/_index.md', 'overview/components.md', 'overview/kubectl.md',
                      'overview/kubernetes-api.md', 'overview/working-with-objects/_index.md'],
}
PREFIX = {'APP_ENG': 'APP', 'PLATFORM_ENG': 'PLAT', 'SECURITY_ENG': 'SEC', 'ALL_EMPLOYEES': 'SHARED'}


def title_of(text, fallback):
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, re.M)
    return m.group(1) if m else fallback


def main():
    (ROOT / 'data/docs').mkdir(parents=True, exist_ok=True)
    manifest, counters = [], {}
    for group, paths in SELECTION.items():
        for rel in paths:
            full = BASE + rel
            try:
                text = urllib.request.urlopen(RAW + full, timeout=60).read().decode('utf-8')
            except Exception as e:
                sys.exit(f'FAILED {RAW + full}: {e}')
            n = counters[group] = counters.get(group, 0) + 1
            doc_id = f'{PREFIX[group]}-{n:03d}'
            fname = full.replace('/', '__')
            (ROOT / 'data/docs' / fname).write_text(text, encoding='utf-8')
            page = full[:-3].replace('/_index', '') + '/'
            manifest.append({
                'document_id': doc_id, 'title': title_of(text, rel), 'filename': rel.split('/')[-1],
                'source_path': 'content/en/docs/' + full, 'github_url': GH + full,
                'source_url': SITE + page, 'access_group': group, 'local_file': 'data/docs/' + fname,
                'license': 'CC BY 4.0 (c) The Kubernetes Authors',
            })
            print(f'{doc_id:11} {manifest[-1]["title"]}')
    (ROOT / 'data/manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Saved {len(manifest)} documents')


if __name__ == '__main__':
    main()
