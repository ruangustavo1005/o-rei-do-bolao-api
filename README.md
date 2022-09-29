# O Rei do Bolao

# 🐳 Docker

## 🐳 Docker Compose

### 🐳 Docker Compose - Up
    
```bash
docker-compose up -d
```

### 🐳 Docker Compose - Down
    
```bash
docker-compose down
```

### 🐳 Docker Compose - Build

Subir containers e refazer build

```
-d, --detach        Detached mode: Run containers in the background,
                        print new container names. Incompatible with
                        --abort-on-container-exit.
--no-deps           Don't start linked services.
--force-recreate    Recreate containers even if their configuration
                        and image haven't changed.
--build  
```

```bash
docker-compose up -d --build --force-recreate --no-deps
```