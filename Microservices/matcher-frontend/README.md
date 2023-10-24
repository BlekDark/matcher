# Matcher Frontend
<br>

## Docker Container Setup

### 1. Build the Docker image:
```sh
docker build -t matcher-frontend .
```

### 2. Run the Docker container:
```shell
docker run -d --rm -p 5173:80 --name frontend-container matcher-frontend
```
<br>

Open your web browser and navigate to http://localhost:5173 to access the frontend application.

<br>

## Project Setup for development

### Install the dependencies:
```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```
**Note:** Production files are located in the `dist` folder
