# Linux 环境 Docker 安装指南

## 📋 目录

- [前置检查](#前置检查)
- [Ubuntu/Debian 系统安装](#ubuntudebian-系统安装)
- [CentOS/RHEL 系统安装](#centosrhel-系统安装)
- [验证安装](#验证安装)
- [配置 Docker 权限](#配置-docker-权限)
- [启动 Dixiyang 项目](#启动-dixiyang-项目)
- [常见问题](#常见问题)

---

## 🔍 前置检查

首先检查系统是否已安装 Docker：

```bash
# 检查 Docker 是否已安装
docker --version

# 检查 Docker Compose 是否已安装
docker compose version
```

如果显示版本号，说明已安装，可以跳过安装步骤。

---

## 🐧 Ubuntu/Debian 系统安装

### 方法一：使用官方脚本（推荐，最简单）

```bash
# 下载并执行 Docker 官方安装脚本
curl -fsSL https://get.docker.com | sudo sh

# 等待安装完成后，启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 方法二：手动安装（适合需要精细控制的情况）

```bash
# 1. 更新包索引
sudo apt-get update

# 2. 安装必要的依赖包
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. 设置 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 更新包索引
sudo apt-get update

# 6. 安装 Docker Engine、CLI、Containerd 和 Docker Compose Plugin
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 7. 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 针对 Debian 系统

如果是 Debian 系统，将第 3、4 步中的 `ubuntu` 替换为 `debian`：

```bash
# 添加 GPG 密钥
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

---

## 🎩 CentOS/RHEL 系统安装

### 方法一：使用官方脚本（推荐）

```bash
# 下载并执行 Docker 官方安装脚本
curl -fsSL https://get.docker.com | sudo sh

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 方法二：手动安装

```bash
# 1. 安装必要的依赖包
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 2. 添加 Docker 官方仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. 安装 Docker Engine、CLI、Containerd
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 4. 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 5. 验证安装
docker --version
```

---

## ✅ 验证安装

安装完成后，运行以下命令验证：

```bash
# 1. 检查 Docker 版本
docker --version
# 预期输出：Docker version 24.x.x, build xxxxxxx

# 2. 检查 Docker Compose 版本
docker compose version
# 预期输出：Docker Compose version v2.x.x

# 3. 运行测试容器
sudo docker run hello-world
# 预期输出：Hello from Docker! 等信息

# 4. 检查 Docker 服务状态
sudo systemctl status docker
# 应该显示 active (running)
```

---

## 🔑 配置 Docker 权限（重要）

默认情况下，Docker 需要 root 权限才能运行。为了避免每次都使用 `sudo`，建议将当前用户加入 docker 组：

```bash
# 1. 创建 docker 组（如果不存在）
sudo groupadd docker

# 2. 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 3. 激活组更改（选择以下任一方法）

# 方法 A：重新登录系统（最可靠）
# 注销后重新登录

# 方法 B：刷新当前会话
newgrp docker

# 4. 验证无需 sudo 即可运行 Docker
docker run hello-world
```

**注意**：如果执行 `newgrp docker` 后仍然需要 sudo，请注销并重新登录系统。

---

## 🚀 启动 Dixiyang 项目

### 1. 克隆或进入项目目录

```bash
# 如果还没有克隆项目
git clone https://github.com/your-username/Dixiyang.git
cd Dixiyang

# 如果已经克隆，直接进入项目目录
cd /path/to/Dixiyang
```

### 2. 复制 Docker Compose 配置文件

```bash
# 将 docker-compose.yml 复制到项目根目录
cp dixiyang-engine/src/main/resources/docker-compose.yml ./docker-compose.yml
```

### 3. 启动 Qdrant 服务

```bash
# 启动所有服务（后台运行）
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f qdrant
```

### 4. 验证服务

```bash
# 访问 Qdrant Web UI（在浏览器中打开）
# http://localhost:6333/dashboard

# 或使用 curl 测试 API
curl http://localhost:6333/collections
```

预期返回：
```json
{"result":{"collections":[]},"status":"ok","time":0.000xxx}
```

### 5. 停止服务

```bash
# 停止服务（保留数据）
docker compose down

# 停止服务并删除数据卷（⚠️ 数据会丢失）
docker compose down -v
```

---

## ❓ 常见问题

### 问题 1：权限被拒绝 (Permission denied)

**错误信息**：
```
Got permission denied while trying to connect to the Docker daemon socket
```

**解决方案**：
```bash
# 确保已将用户加入 docker 组
sudo usermod -aG docker $USER

# 注销并重新登录，或执行
newgrp docker

# 验证
docker run hello-world
```

### 问题 2：Docker 服务未启动

**错误信息**：
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**解决方案**：
```bash
# 启动 Docker 服务
sudo systemctl start docker

# 设置开机自启
sudo systemctl enable docker

# 检查状态
sudo systemctl status docker
```

### 问题 3：端口已被占用

**错误信息**：
```
Error starting userland proxy: listen tcp4 0.0.0.0:6333: bind: address already in use
```

**解决方案**：
```bash
# 查找占用端口的进程
sudo lsof -i :6333
# 或
sudo netstat -tlnp | grep 6333

# 停止占用端口的进程
sudo kill -9 <PID>

# 或者修改 docker-compose.yml 中的端口映射
# 例如将 "6333:6333" 改为 "6335:6333"
```

### 问题 4：网络连接超时

**错误信息**：
```
timeout: failed to connect service
```

**解决方案**：
```bash
# 检查防火墙设置
sudo ufw status

# 如果需要，允许 Docker 相关端口
sudo ufw allow 6333/tcp
sudo ufw allow 6334/tcp

# 或者临时关闭防火墙测试
sudo ufw disable
```

### 问题 5：磁盘空间不足

**错误信息**：
```
no space left on device
```

**解决方案**：
```bash
# 清理未使用的 Docker 资源
docker system prune -a

# 查看 Docker 磁盘使用情况
docker system df

# 清理卷（⚠️ 会删除所有未使用的卷和数据）
docker volume prune
```

### 问题 6：CentOS 上 SELinux 阻止 Docker

**解决方案**：
```bash
# 临时禁用 SELinux
sudo setenforce 0

# 或永久禁用（编辑 /etc/selinux/config）
sudo sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

# 重启系统
sudo reboot
```

### 问题 7：Docker Compose 命令找不到

**错误信息**：
```
docker: 'compose' is not a docker command
```

**解决方案**：

对于较旧的 Docker 版本，需要单独安装 Docker Compose：

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version

# 使用时用 docker-compose 代替 docker compose
docker-compose up -d
```

---

## 📚 相关资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [Docker Hub - Qdrant](https://hub.docker.com/r/qdrant/qdrant)

---

## 📝 快速参考命令

```bash
# Docker 基本命令
docker --version              # 查看版本
docker info                   # 查看系统信息
docker ps                     # 查看运行中的容器
docker ps -a                  # 查看所有容器
docker images                 # 查看镜像
docker logs <container>       # 查看容器日志

# Docker Compose 命令
docker compose up -d          # 后台启动
docker compose down           # 停止并删除
docker compose ps             # 查看状态
docker compose logs -f        # 查看日志
docker compose restart        # 重启服务
docker compose pull           # 拉取最新镜像

# 系统管理
sudo systemctl start docker   # 启动 Docker
sudo systemctl stop docker    # 停止 Docker
sudo systemctl restart docker # 重启 Docker
sudo systemctl status docker  # 查看状态
sudo systemctl enable docker  # 开机自启
```

---

**最后更新**: 2026-06-01
