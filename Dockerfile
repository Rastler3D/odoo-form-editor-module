FROM odoo:17.0

ARG LOCALE=en_US.UTF-8

ENV LANGUAGE=${LOCALE}
ENV LC_ALL=${LOCALE}
ENV LANG=${LOCALE}

USER 0

RUN apt-get -y update && apt-get install -y --no-install-recommends locales netcat-openbsd \
    && locale-gen ${LOCALE}

COPY --chmod=755 custom-addons /opt/odoo/addons
COPY --chmod=755 odoo.conf /opt/odoo/odoo.conf

WORKDIR /app
COPY --chmod=755 entrypoint.sh ./


ENTRYPOINT ["/bin/sh"]

CMD ["entrypoint.sh"]