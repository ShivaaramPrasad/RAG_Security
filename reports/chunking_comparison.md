# Chunking comparison (30 Kubernetes docs, identical cleaned input)

| Metric | fixed | recursive | markdown | semantic |
|---|---|---|---|---|
| Total chunks | 672 | 732 | 736 | 530 |
| Average size (chars) | 980 | 800 | 819 | 1059 |
| Median size | 1000 | 850 | 830 | 1121 |
| Minimum size | 154 | 114 | 85 | 30 |
| Maximum size | 1000 | 1000 | 2040 | 11882 |
| Chunks carrying heading context (%) | 65.0 | 60.0 | 100.0 | 64.5 |
| Chunks starting on a clean boundary (%) | 6.0 | 82.9 | 90.6 | 96.0 |
| Chunks ending on a clean boundary (%) | 5.2 | 87.8 | 94.0 | 100.0 |
| Chunks with a broken code fence | 82 | 12 | 8 | 0 |
| Tiny chunks (<150 chars) | 0 | 2 | 2 | 3 |
| Oversize chunks (>1500 chars) | 0 | 0 | 1 | 14 |
| Overlap | 150 chars | 150 chars | none | none |

## Configuration

- **fixed**: size=1000, overlap=150
- **recursive**: size=1000, overlap=150, seps: ## / ### / #### / blank line / line / sentence / space
- **markdown**: max=1200, min section=250, heading path prefix, code fences never split
- **semantic**: block embeddings, split above 85th-percentile cosine distance, min=300, max=1500

## Boundary examples

### fixed
- **Good boundary** (PLAT-006): `This document describes _ephemeral volumes_ in Kubernetes. Familiarity\nwith [volumes](/docs/concepts/storage/volumes/) is suggested, in\nparticular PersistentVolumeClaim and PersistentVolume.\n\nSome applications need additional storage but don't care whether...`
- **Poor boundary** (APP-001): `A _Deployment_ provides declarative updates for Pods and\nReplicaSets.\n\nYou describe a _desired state_ in a Deployment, and the Deployment  changes the actual state to the desired state at a controlled rate. You can define Deployments to create new ReplicaSe...`

### recursive
- **Good boundary** (APP-001): `**Note:**\nYou must specify an appropriate selector and Pod template labels in a Deployment\n(in this case, `app: nginx`).\n\nDo not overlap labels or selectors with other controllers (including other Deployments and StatefulSets). Kubernetes doesn't stop you ...`
- **Poor boundary** (APP-001): `A _Deployment_ provides declarative updates for Pods and\nReplicaSets.\n\nYou describe a _desired state_ in a Deployment, and the Deployment  changes the actual state to the desired state at a controlled rate. You can define Deployments to create new ReplicaSe...`

### markdown
- **Good boundary** (APP-001): `Deployments\n\nA _Deployment_ provides declarative updates for Pods and\nReplicaSets.\n\nYou describe a _desired state_ in a Deployment, and the Deployment  changes the actual state to the desired state at a controlled rate. You can define Deployments to creat...`
- **Poor boundary** (APP-001): `Deployments > Creating a Deployment\n\n  **Note:**\n  The `.spec.selector.matchLabels` field is a map of {key,value} pairs.\n  A single {key,value} in the `matchLabels` map is equivalent to an element of `matchExpressions`,\n  whose `key` field is "key", the `...`

### semantic
- **Good boundary** (APP-001): `## Use Case\n\nThe following are typical use cases for Deployments:\n\n* [Create a Deployment to rollout a ReplicaSet](#creating-a-deployment). The ReplicaSet creates Pods in the background. Check the status of the rollout to see if it succeeds or not.\n* [Dec...`
- **Poor boundary** (APP-001): `   Notice that the name of the ReplicaSet is always formatted as\n   `[DEPLOYMENT-NAME]-[HASH]`. This name will become the basis for the Pods\n   which are created.\n\n   The `HASH` string is the same as the `pod-template-hash` label on the ReplicaSet.\n\n6. T...`
