{{- define "labshelf.labels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: labshelf
{{- end }}
