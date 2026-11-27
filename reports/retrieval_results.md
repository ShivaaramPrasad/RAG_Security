# Exercise D - same question, different identities

Distances are cosine distances (lower = closer). "Authorized" = the row survived database RLS. "Withheld" rows come from an admin audit of the unfiltered ranking and were **never returned** to the user.

## How does a Kubernetes Deployment manage application replicas?
*Primary knowledge area: Application Engineering*

### Priya (APP_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | APP-001 | Deployments | 0.1577 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | yes |
| 2 | APP-002 | ReplicaSet | 0.1671 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | yes |
| 3 | APP-001 | Deployments > Writing a Deployment Spec > Replicas | 0.1718 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | yes |
| 4 | APP-002 | ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) | 0.1985 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | yes |
| 5 | SHARED-005 | Objects In Kubernetes > Understanding Kubernetes objects > Object spec and status | 0.2128 | https://kubernetes.io/docs/concepts/overview/working-with-objects/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Priya

### Arjun (PLATFORM_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-005 | Objects In Kubernetes > Understanding Kubernetes objects > Object spec and status | 0.2128 | https://kubernetes.io/docs/concepts/overview/working-with-objects/ | yes |
| 2 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2238 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2306 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 4 | SHARED-001 | Overview > Historical context for Kubernetes | 0.2320 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 5 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2436 | https://kubernetes.io/docs/concepts/overview/ | yes |

Admin audit of the unfiltered top-5: 4 withheld from Arjun: APP-001 [APP_ENG] dist 0.1577, APP-002 [APP_ENG] dist 0.1671, APP-001 [APP_ENG] dist 0.1718, APP-002 [APP_ENG] dist 0.1985

### Meena (SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-005 | Objects In Kubernetes > Understanding Kubernetes objects > Object spec and status | 0.2128 | https://kubernetes.io/docs/concepts/overview/working-with-objects/ | yes |
| 2 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2238 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2306 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 4 | SHARED-001 | Overview > Historical context for Kubernetes | 0.2320 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 5 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2436 | https://kubernetes.io/docs/concepts/overview/ | yes |

Admin audit of the unfiltered top-5: 4 withheld from Meena: APP-001 [APP_ENG] dist 0.1577, APP-002 [APP_ENG] dist 0.1671, APP-001 [APP_ENG] dist 0.1718, APP-002 [APP_ENG] dist 0.1985

### Divya (APP_ENG, SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | APP-001 | Deployments | 0.1577 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | yes |
| 2 | APP-002 | ReplicaSet | 0.1671 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | yes |
| 3 | APP-001 | Deployments > Writing a Deployment Spec > Replicas | 0.1718 | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | yes |
| 4 | APP-002 | ReplicaSet > Alternatives to ReplicaSet > Deployment (recommended) | 0.1985 | https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/ | yes |
| 5 | SHARED-005 | Objects In Kubernetes > Understanding Kubernetes objects > Object spec and status | 0.2128 | https://kubernetes.io/docs/concepts/overview/working-with-objects/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Divya

## What are PersistentVolumes and PersistentVolumeClaims?
*Primary knowledge area: Platform Engineering*

### Priya (APP_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | APP-003 | StatefulSets > Pod Identity > Stable Storage | 0.2278 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 2 | APP-003 | StatefulSets > PersistentVolumeClaim retention | 0.2927 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 3 | APP-003 | StatefulSets > PersistentVolumeClaim retention | 0.2950 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 4 | APP-003 | StatefulSets > Components > Pod Selector | 0.2998 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 5 | APP-003 | StatefulSets > PersistentVolumeClaim retention | 0.3077 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |

Admin audit of the unfiltered top-5: 4 withheld from Priya: PLAT-002 [PLATFORM_ENG] dist 0.1820, PLAT-002 [PLATFORM_ENG] dist 0.2114, PLAT-002 [PLATFORM_ENG] dist 0.2204, PLAT-001 [PLATFORM_ENG] dist 0.2250

### Arjun (PLATFORM_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | PLAT-002 | Persistent Volumes > Introduction | 0.1820 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | yes |
| 2 | PLAT-002 | Persistent Volumes > Introduction | 0.2114 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | yes |
| 3 | PLAT-002 | Persistent Volumes > PersistentVolumeClaims | 0.2204 | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ | yes |
| 4 | PLAT-001 | Volumes > Types of volumes > Volumes that use a PersistentVolumeClaim | 0.2250 | https://kubernetes.io/docs/concepts/storage/volumes/ | yes |
| 5 | PLAT-005 | Volume Snapshots > Lifecycle of a volume snapshot and volume snapshot content > Persistent Volume Claim as Snapshot Source Protection | 0.2302 | https://kubernetes.io/docs/concepts/storage/volume-snapshots/ | yes |

Admin audit of the unfiltered top-5: 1 withheld from Arjun: APP-003 [APP_ENG] dist 0.2278

### Meena (SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SEC-001 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Persistent volume creation | 0.2983 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |
| 2 | SEC-005 | Multi-tenancy > Data Plane Isolation > Storage isolation | 0.3086 | https://kubernetes.io/docs/concepts/security/multi-tenancy/ | yes |
| 3 | SHARED-004 | The Kubernetes API > Persistence | 0.3770 | https://kubernetes.io/docs/concepts/overview/kubernetes-api/ | yes |
| 4 | SHARED-005 | Objects In Kubernetes | 0.4070 | https://kubernetes.io/docs/concepts/overview/working-with-objects/ | yes |
| 5 | SEC-005 | Multi-tenancy > Data Plane Isolation > Storage isolation | 0.4086 | https://kubernetes.io/docs/concepts/security/multi-tenancy/ | yes |

Admin audit of the unfiltered top-5: 5 withheld from Meena: PLAT-002 [PLATFORM_ENG] dist 0.1820, PLAT-002 [PLATFORM_ENG] dist 0.2114, PLAT-002 [PLATFORM_ENG] dist 0.2204, PLAT-001 [PLATFORM_ENG] dist 0.2250, APP-003 [APP_ENG] dist 0.2278

### Divya (APP_ENG, SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | APP-003 | StatefulSets > Pod Identity > Stable Storage | 0.2278 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 2 | APP-003 | StatefulSets > PersistentVolumeClaim retention | 0.2927 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 3 | APP-003 | StatefulSets > PersistentVolumeClaim retention | 0.2950 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |
| 4 | SEC-001 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks > Persistent volume creation | 0.2983 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |
| 5 | APP-003 | StatefulSets > Components > Pod Selector | 0.2998 | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | yes |

Admin audit of the unfiltered top-5: 4 withheld from Divya: PLAT-002 [PLATFORM_ENG] dist 0.1820, PLAT-002 [PLATFORM_ENG] dist 0.2114, PLAT-002 [PLATFORM_ENG] dist 0.2204, PLAT-001 [PLATFORM_ENG] dist 0.2250

## What are recommended Kubernetes RBAC practices?
*Primary knowledge area: Security Engineering*

### Priya (APP_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-001 | Overview | 0.2534 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 2 | SHARED-001 | Overview > What Kubernetes is not | 0.2884 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2916 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 4 | SHARED-001 | Overview > Historical context for Kubernetes | 0.2978 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 5 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.3044 | https://kubernetes.io/docs/concepts/overview/ | yes |

Admin audit of the unfiltered top-5: 5 withheld from Priya: SEC-001 [SECURITY_ENG] dist 0.1553, SEC-004 [SECURITY_ENG] dist 0.2120, SEC-005 [SECURITY_ENG] dist 0.2172, SEC-001 [SECURITY_ENG] dist 0.2493, SEC-001 [SECURITY_ENG] dist 0.2494

### Arjun (PLATFORM_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-001 | Overview | 0.2534 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 2 | SHARED-001 | Overview > What Kubernetes is not | 0.2884 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.2916 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 4 | SHARED-001 | Overview > Historical context for Kubernetes | 0.2978 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 5 | SHARED-001 | Overview > Why you need Kubernetes and what it can do | 0.3044 | https://kubernetes.io/docs/concepts/overview/ | yes |

Admin audit of the unfiltered top-5: 5 withheld from Arjun: SEC-001 [SECURITY_ENG] dist 0.1553, SEC-004 [SECURITY_ENG] dist 0.2120, SEC-005 [SECURITY_ENG] dist 0.2172, SEC-001 [SECURITY_ENG] dist 0.2493, SEC-001 [SECURITY_ENG] dist 0.2494

### Meena (SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SEC-001 | Role Based Access Control Good Practices | 0.1553 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |
| 2 | SEC-004 | Good practices for Kubernetes Secrets > Cluster administrators > Configure least-privilege access to Secrets | 0.2120 | https://kubernetes.io/docs/concepts/security/secrets-good-practices/ | yes |
| 3 | SEC-005 | Multi-tenancy > Control plane isolation > Access controls | 0.2172 | https://kubernetes.io/docs/concepts/security/multi-tenancy/ | yes |
| 4 | SEC-001 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks | 0.2493 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |
| 5 | SEC-001 | Role Based Access Control Good Practices > General good practice > Periodic review | 0.2494 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Meena

### Divya (APP_ENG, SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SEC-001 | Role Based Access Control Good Practices | 0.1553 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |
| 2 | SEC-004 | Good practices for Kubernetes Secrets > Cluster administrators > Configure least-privilege access to Secrets | 0.2120 | https://kubernetes.io/docs/concepts/security/secrets-good-practices/ | yes |
| 3 | SEC-005 | Multi-tenancy > Control plane isolation > Access controls | 0.2172 | https://kubernetes.io/docs/concepts/security/multi-tenancy/ | yes |
| 4 | SEC-001 | Role Based Access Control Good Practices > Kubernetes RBAC - privilege escalation risks | 0.2493 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |
| 5 | SEC-001 | Role Based Access Control Good Practices > General good practice > Periodic review | 0.2494 | https://kubernetes.io/docs/concepts/security/rbac-good-practices/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Divya

## What are the main Kubernetes components?
*Primary knowledge area: Shared knowledge*

### Priya (APP_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-002 | Kubernetes Components | 0.1199 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 2 | SHARED-001 | Overview | 0.1502 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-002 | Kubernetes Components > Core Components > Control Plane Components | 0.2021 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 4 | SHARED-002 | Kubernetes Components > Flexibility in Architecture | 0.2141 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 5 | SHARED-002 | Kubernetes Components > Core Components > Node Components | 0.2271 | https://kubernetes.io/docs/concepts/overview/components/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Priya

### Arjun (PLATFORM_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-002 | Kubernetes Components | 0.1199 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 2 | SHARED-001 | Overview | 0.1502 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-002 | Kubernetes Components > Core Components > Control Plane Components | 0.2021 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 4 | SHARED-002 | Kubernetes Components > Flexibility in Architecture | 0.2141 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 5 | SHARED-002 | Kubernetes Components > Core Components > Node Components | 0.2271 | https://kubernetes.io/docs/concepts/overview/components/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Arjun

### Meena (SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-002 | Kubernetes Components | 0.1199 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 2 | SHARED-001 | Overview | 0.1502 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-002 | Kubernetes Components > Core Components > Control Plane Components | 0.2021 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 4 | SHARED-002 | Kubernetes Components > Flexibility in Architecture | 0.2141 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 5 | SHARED-002 | Kubernetes Components > Core Components > Node Components | 0.2271 | https://kubernetes.io/docs/concepts/overview/components/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Meena

### Divya (APP_ENG, SECURITY_ENG + shared)

| Rank | Document | Heading | Cosine dist. | Source link | Authorized |
|---|---|---|---|---|---|
| 1 | SHARED-002 | Kubernetes Components | 0.1199 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 2 | SHARED-001 | Overview | 0.1502 | https://kubernetes.io/docs/concepts/overview/ | yes |
| 3 | SHARED-002 | Kubernetes Components > Core Components > Control Plane Components | 0.2021 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 4 | SHARED-002 | Kubernetes Components > Flexibility in Architecture | 0.2141 | https://kubernetes.io/docs/concepts/overview/components/ | yes |
| 5 | SHARED-002 | Kubernetes Components > Core Components > Node Components | 0.2271 | https://kubernetes.io/docs/concepts/overview/components/ | yes |

Admin audit of the unfiltered top-5: 0 withheld from Divya
