FROM python:3.11

ARG DOCKER_USER=mmisp
ARG INSTALL_LIB=false
ARG LIB_REPO_URL
ARG BRANCH

RUN groupadd "$DOCKER_USER"
RUN useradd -ms /bin/bash -g "$DOCKER_USER" "$DOCKER_USER"

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

ADD --chown=$DOCKER_USER:$DOCKER_USER . ./
RUN pip install '.[dev]'
RUN pip install 'gunicorn'
RUN pip install 'uvicorn-worker'
# also install lib
RUN if [ "$INSTALL_LIB" = "true" ]; then \
      if git ls-remote --exit-code --heads $LIB_REPO_URL $BRANCH; then \
        pip install --force-reinstall git+${LIB_REPO_URL}@${BRANCH}; \
      else \
        pip install --force-reinstall git+${LIB_REPO_URL}@main; \
      fi \
    fi

EXPOSE 4000
CMD ["/entrypoint.sh"]
