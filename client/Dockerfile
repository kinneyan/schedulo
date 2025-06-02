# Use the official Node.js image as the base
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (or pnpm/yarn lock files) to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire project into the container
COPY . .

# Default command to switch between development and production
CMD ["sh", "-c", "if [ \"$REACT_ENV\" = \"production\" ]; then \
  npm run build && cp -r dist/* /usr/share/nginx/html; \
  else \
  npm run dev -- --host; \
  fi"]
