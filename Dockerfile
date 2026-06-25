FROM ghcr.io/soju06/codex-lb:latest

USER root
COPY patch-clipboard.py /tmp/patch-clipboard.py
COPY patch-models-compat.py /tmp/patch-models-compat.py
COPY patch-context-overflow.py /tmp/patch-context-overflow.py
COPY patch-oauth-provider.py /tmp/patch-oauth-provider.py
COPY patch-oauth-dialog-provider.py /tmp/patch-oauth-dialog-provider.py
COPY patch-overload-failover.py /tmp/patch-overload-failover.py
COPY patch-auto-model-routing.py /tmp/patch-auto-model-routing.py
COPY patch-weekly-remaining.py /tmp/patch-weekly-remaining.py
COPY patch-plan-capacities.py /tmp/patch-plan-capacities.py
COPY patch-plan-guard.py /tmp/patch-plan-guard.py
COPY patch-dashboard-live-usage.py /tmp/patch-dashboard-live-usage.py
COPY patch-plan-priority-routing.py /tmp/patch-plan-priority-routing.py
COPY patch-live-account-usage.py /tmp/patch-live-account-usage.py
COPY patch-http-bridge-plan-priority.py /tmp/patch-http-bridge-plan-priority.py
COPY patch-oauth-reauth-target.py /tmp/patch-oauth-reauth-target.py
RUN python /tmp/patch-clipboard.py \
    && python /tmp/patch-models-compat.py \
    && python /tmp/patch-context-overflow.py \
    && python /tmp/patch-oauth-provider.py \
    && python /tmp/patch-oauth-dialog-provider.py \
    && python /tmp/patch-overload-failover.py \
    && python /tmp/patch-auto-model-routing.py \
    && python /tmp/patch-weekly-remaining.py \
    && python /tmp/patch-plan-capacities.py \
    && python /tmp/patch-plan-guard.py \
    && python /tmp/patch-live-account-usage.py \
    && python /tmp/patch-plan-priority-routing.py \
    && python /tmp/patch-http-bridge-plan-priority.py \
    && python /tmp/patch-oauth-reauth-target.py \
    && python /tmp/patch-dashboard-live-usage.py \
    && rm /tmp/patch-clipboard.py /tmp/patch-models-compat.py /tmp/patch-context-overflow.py /tmp/patch-oauth-provider.py /tmp/patch-oauth-dialog-provider.py /tmp/patch-overload-failover.py /tmp/patch-auto-model-routing.py /tmp/patch-weekly-remaining.py /tmp/patch-plan-capacities.py /tmp/patch-plan-guard.py /tmp/patch-live-account-usage.py /tmp/patch-plan-priority-routing.py /tmp/patch-http-bridge-plan-priority.py /tmp/patch-oauth-reauth-target.py /tmp/patch-dashboard-live-usage.py
USER app
