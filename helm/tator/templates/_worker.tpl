{{ define "worker.template" }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  labels:
    app: {{ .app }}
    type: web
spec:
  selector:
    matchLabels:
      app: {{ .app }}
      type: web
  replicas: {{ .replicas }}
  template:
    metadata:
      labels:
        app: {{ .app }}
        type: web
    spec:
      terminationGracePeriodSeconds: 60
      nodeSelector:
        {{ .selector }}
      containers:
        - name: tator-online
          image: {{ .Values.dockerRegistry }}/tator_online:{{ .Values.gitRevision }}
          imagePullPolicy: "Always"
          command: {{ .command }}
          args: {{ .args }}
          resources:
            limits:
              cpu: {{ .Values.workerCpuLimit | default "1000m" }}
              memory: {{ .Values.workerMemoryLimit | default "1Gi" }}
            requests:
              cpu: {{ .Values.workerCpuRequest | default "1000m" }}
              memory: {{ .Values.workerMemoryRequest | default "1Gi" }}
          env:
            {{include "tatorEnv.template" . | indent 12 }}
          volumeMounts:
            {{ include "volumeMounts.template" . | indent 12 }}
            {{- if .Values.cognito.enabled }}
            - mountPath: /cognito
              name: cognito-config
              readOnly: true
            {{- end }}
      initContainers:
        - name: redis
          image: redis
          imagePullPolicy: "IfNotPresent"
          command: ["redis-cli"]
          args: ["-h", {{ .Values.redisHost | quote }}, "-p", "6379", "ping"]
      volumes:
        {{ include "volumes.template" . | indent 8 }}
        {{- if .Values.cognito.enabled }}
        - name: cognito-config
          secret:
            secretName: tator-secrets
            items:
              - key: cognito-config
                path: cognito.yaml
        {{- end }}
{{ end }}
