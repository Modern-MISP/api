FROM python:3.11

ARG DOCKER_USER=mmisp
ARG INSTALL_LIB=false
ARG LIB_REPO_URL
ARG BRANCH

RUN groupadd "$DOCKER_USER"
RUN useradd -ms /bin/bash -g "$DOCKER_USER" "$DOCKER_USER"
USER $DOCKER_USER
WORKDIR /home/$DOCKER_USER

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/${DOCKER_USER}/.local/bin:${PATH}"

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
CMD ["gunicorn", "mmisp.api.main:app", "-b", "0.0.0.0:4000", "-w", "4", "-k", "uvicorn_worker.UvicornWorker"]
