# 使用腾讯的dockerhub服务

## 登录

[腾讯云大陆个人仓库控制台](https://console.cloud.tencent.com/tcr/instance?rid=1)

点击"登录实例" 复制

`docker login ccr.ccs.tencentyun.com --username=XXXXXX`

## 打包
```bash
# 本地打包
export TAG_VERSION="0.3"

docker build -t gy-mall-backend:$TAG_VERSION .

# 打腾讯云的tag
docker tag gy-mall-backend:$TAG_VERSION ccr.ccs.tencentyun.com/aweffr-main/gy-mall-backend:$TAG_VERSION

# Push
docker push ccr.ccs.tencentyun.com/aweffr-main/gy-mall-backend:$TAG_VERSION
```
