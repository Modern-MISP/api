FROM python:3.12.3-alpine
#FROM python:3.11-slim
RUN apk --no-cache upgrade && apk --no-cache add git

ARG DOCKER_USER=mmisp
ARG INSTALL_LIB=false
ARG LIB_REPO_URL
ARG BRANCH

RUN addgroup -S $DOCKER_USER && adduser -S $DOCKER_USER -G $DOCKER_USER
#RUN groupadd "$DOCKER_USER"
#RUN useradd -ms /bin/bash -g "$DOCKER_USER" "$DOCKER_USER"

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

USER $DOCKER_USER
WORKDIR /home/$DOCKER_USER

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/${DOCKER_USER}/.local/bin:${PATH}"
# set to empty if you dont want a db setup
ENV SETUP_DB="1"
#ENV COVERAGE_CORE=sysmon

ADD --chown=$DOCKER_USER:$DOCKER_USER . ./
RUN pip install --no-cache-dir '.[dev]'
RUN pip install --no-cache-dir  'gunicorn'
RUN pip install --no-cache-dir  'uvicorn-worker'
# also install lib
RUN if [ "$INSTALL_LIB" = "true" ]; then \
      if git ls-remote --exit-code --heads $LIB_REPO_URL $BRANCH; then \
        pip install --no-cache-dir  --force-reinstall git+${LIB_REPO_URL}@${BRANCH}; \
      else \
        pip install --no-cache-dir  --force-reinstall git+${LIB_REPO_URL}@main; \
      fi \
    fi

EXPOSE 4000

USER root
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
USER $DOCKER_USER

CMD ["/entrypoint.sh"]
