#!/bin/bash

# Define the name of your new Next.js app directory
# This will be created in the directory where you run this script.
APP_NAME="app"

# --- Step 1: Create temporary Dockerfile for boilerplate generation ---
echo "Creating temporary Dockerfile for boilerplate generation..."
mkdir -p temp-next-app-generator
cat <<EOF > temp-next-app-generator/Dockerfile
FROM node:20-alpine
WORKDIR /app
EOF

# --- Step 2: Build the temporary Docker image ---
echo "Building temporary Docker image 'next-app-generator'..."
docker build -t next-app-generator -f temp-next-app-generator/Dockerfile temp-next-app-generator

# --- Step 3: Generate Next.js app boilerplate inside a Docker container ---
echo "Generating Next.js app boilerplate into './$APP_NAME' on your host machine..."
echo "This will use: TypeScript, ESLint, Tailwind CSS, App Router, src directory, '@/*' import alias, skip Git initialization, and run non-interactively (CI mode)."

docker run --rm \
  -e CI=true \
  -v "$(pwd):/data" \
  next-app-generator \
  sh -c "npx create-next-app@latest /data/$APP_NAME --ts --eslint --tailwind --app --src-dir --import-alias '@/*' --use-npm --skip-git"

# Explanation of `create-next-app` flags:
#   --ts:          Initialize project with TypeScript.
#   --eslint:      Initialize project with ESLint.
#   --tailwind:    Initialize project with Tailwind CSS.
#   --app:         Use the App Router (recommended for Next.js 13+).
#   --src-dir:     Organize your project with a `src/` directory.
#   --import-alias '@/*': Configure the `@/*' import alias.
#   --use-npm:     Explicitly use npm for package management.
#   --skip-git:    Skip initializing a Git repository.
#   CI=true:       This environment variable makes many CLI tools (including create-next-app)
#                  run in a non-interactive mode, typically choosing default answers.

# --- Step 4: Verify and Cleanup ---
if [ -d "./$APP_NAME" ]; then
  echo "============================================================"
  echo "✅ Next.js app '$APP_NAME' successfully generated!"
  echo "   You can now navigate into './$APP_NAME' and start developing."
  echo "   (e.g., 'cd $APP_NAME' then 'npm install' if not using Docker Compose, or proceed with Docker Compose)"
  echo "============================================================"
else
  echo "============================================================"
  echo "❌ Error: Next.js app '$APP_NAME' was not generated."
  echo "   Please check the output above for any errors during 'docker run'."
  echo "============================================================"
  exit 1
fi

echo "Cleaning up temporary Dockerfile directory..."
rm -rf temp-next-app-generator

echo "Removing temporary Docker image 'next-app-generator'..."
docker rmi next-app-generator > /dev/null 2>&1
echo "Cleanup complete."