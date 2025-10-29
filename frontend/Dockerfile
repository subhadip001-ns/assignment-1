# Single stage build - install all deps and build in one go
FROM node:22-alpine

# Install pnpm
RUN npm install -g pnpm

# Set work directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install ALL dependencies (including dev deps for building)
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm build

# Expose port and map port 4173 to port 5173
EXPOSE 4173

# Serve the built application using Vite preview
CMD ["pnpm", "start", "--host", "0.0.0.0", "--port", "4173"]