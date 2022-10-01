# O Rei do Bolão

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

## 🤝 Agradecimentos 

* ao [@almirb](https://github.com/almirb), colega de trabalho que me disponibilizou o acesso dele de um curso (pago) de visão computacional que me deu os conceitos base pra usar no projeto
* ao [@gustavokuhl](https://github.com/gustavokuhl), por me ceder toda consultoria de python, docker, e tudo que mais fosse necessário
