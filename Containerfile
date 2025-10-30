FROM docker.io/library/debian:trixie

LABEL org.opencontainers.image.source https://github.com/zc-mattcen/debian-runner

ARG USERNAME=debian
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt-get --update install -y --no-install-recommends \
    extrepo \
    && sed --in-place -e 's/# - non-free/- non-free/' /etc/extrepo/config.yaml \
    && extrepo enable opentofu \
    && apt-get purge man-db \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get --update install -y --no-install-recommends \
    ansible \
    ansible-lint \
    awscli \
    flake8 \
    git \
    make \
    nodejs \
    python3 \
    python3-boto3 \
    python3-coverage \
    python3-jsonschema \
    python3-pytest \
    python3-pytest-cov \
    python3-virtualenv \
    shellcheck \
    sudo \
    tofu=1.10.5 \
    yamllint \
    yq \
    && rm -rf /var/lib/apt/lists/* \
    && apt-mark hold tofu

RUN groupadd --gid "$USER_GID" "$USERNAME" \
    && useradd --uid "$USER_UID" --gid "$USER_GID" --create-home "$USERNAME" \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/$USERNAME" \
    && chmod 0440 "/etc/sudoers.d/$USERNAME"

USER $USERNAME
