# ─────────────────────────────────────────────────────────────────────────────
# Compose files
# ─────────────────────────────────────────────────────────────────────────────
# DOCKER_COMPOSE_PROD = -f docker-compose.prod.yaml
DOCKER_COMPOSE_DEV  = -f docker-compose.dev.yaml

# ─────────────────────────────────────────────────────────────────────────────
# Env file paths
# ─────────────────────────────────────────────────────────────────────────────
BACKEND_ENV_DEV  = ./backend/.env.dev
DATABASE_ENV_DEV = ./database/.env.dev
# BACKEND_ENV_PROD  = ./backend/.env.docker.prod
# DATABASE_ENV_PROD = ./database/.env.database.prod

# ─────────────────────────────────────────────────────────────────────────────
# Env shorthands
# ─────────────────────────────────────────────────────────────────────────────
ENV_DEV  = BACKEND_ENV_FILE=$(BACKEND_ENV_DEV) DATABASE_ENV_FILE=$(DATABASE_ENV_DEV)
# ENV_PROD = BACKEND_ENV_FILE=$(BACKEND_ENV_PROD) DATABASE_ENV_FILE=$(DATABASE_ENV_PROD)

# ─────────────────────────────────────────────────────────────────────────────
# Dev targets
# ─────────────────────────────────────────────────────────────────────────────

build_dev:
	$(ENV_DEV) docker compose $(DOCKER_COMPOSE_DEV) build

up_dev:
	$(ENV_DEV) docker compose $(DOCKER_COMPOSE_DEV) up -d

down_dev:
	$(ENV_DEV) docker compose $(DOCKER_COMPOSE_DEV) down

logs:
	$(ENV_DEV) docker compose $(DOCKER_COMPOSE_DEV) logs -f

# ─────────────────────────────────────────────────────────────────────────────
# Prod targets (not implemented yet)
# ─────────────────────────────────────────────────────────────────────────────

# build_prod:
# 	$(ENV_PROD) docker compose $(DOCKER_COMPOSE_PROD) build

# up_prod:
# 	$(ENV_PROD) docker compose $(DOCKER_COMPOSE_PROD) up -d

# down_prod:
# 	$(ENV_PROD) docker compose $(DOCKER_COMPOSE_PROD) down
