FROM python:3.11.4-slim as base

FROM base as builder
USER root 

WORKDIR /app
RUN python -m venv .venv && .venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -U pip setuptools
COPY src/ /app/
#RUN apk add --no-cache gcc && \
RUN	.venv/bin/pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt && \
    rm requirements.txt && \
	find /app/.venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+


FROM base
ENV         PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /app /app
RUN apt update -y && apt upgrade -y && apt install git -y
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/.venv/lib/python3.11/site-packages:$PYTHONPATH"
RUN git --version
# Use the nobody user's numeric UID/GID to satisfy MustRunAsNonRoot PodSecurityPolicies
# https://kubernetes.io/docs/concepts/policy/pod-security-policy/#users-and-groups
USER        65534:65534
CMD         [ "python", "-u", "/app/main.py" ]