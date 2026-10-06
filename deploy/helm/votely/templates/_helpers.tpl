{{/* Common labels; call with (dict "root" $ "component" "backend"). */}}
{{- define "votely.labels" -}}
{{ include "votely.selectorLabels" . }}
app.kubernetes.io/version: {{ .root.Values.image.tag | quote }}
app.kubernetes.io/part-of: votely
app.kubernetes.io/managed-by: {{ .root.Release.Service }}
helm.sh/chart: {{ .root.Chart.Name }}-{{ .root.Chart.Version }}
{{- end }}

{{- define "votely.selectorLabels" -}}
app.kubernetes.io/name: votely
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "votely.image" -}}
{{ .root.Values.image.registry }}/{{ .component }}:{{ .root.Values.image.tag }}
{{- end }}

{{/* Restricted pod settings shared by every pod: non-root, default seccomp profile. */}}
{{- define "votely.podSecurityContext" -}}
runAsNonRoot: true
seccompProfile:
  type: RuntimeDefault
{{- end }}

{{/* Restricted container settings: no privilege escalation, no capability, read-only root. */}}
{{- define "votely.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities:
  drop: [ALL]
{{- end }}

{{/* Backend settings, shared by the API and the migrations Job. The database URL is assembled
from the Secret keys by Kubernetes ($(VAR) references), so it never appears in the chart. */}}
{{- define "votely.backendEnv" -}}
- name: DB_USER
  valueFrom:
    secretKeyRef: { name: {{ .Values.database.existingSecret }}, key: username }
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef: { name: {{ .Values.database.existingSecret }}, key: password }
- name: DB_NAME
  valueFrom:
    secretKeyRef: { name: {{ .Values.database.existingSecret }}, key: database }
- name: VOTELY_DATABASE_URL
  value: postgresql+psycopg://$(DB_USER):$(DB_PASSWORD)@{{ .Values.database.host }}:5432/$(DB_NAME)
- name: VOTELY_JWT_SECRET
  valueFrom:
    secretKeyRef: { name: {{ .Values.jwt.existingSecret }}, key: jwt-secret }
- name: VOTELY_COOKIE_SECURE
  value: {{ .Values.cookieSecure | quote }}
- name: VOTELY_LOG_LEVEL
  value: {{ .Values.logLevel | quote }}
{{- end }}
