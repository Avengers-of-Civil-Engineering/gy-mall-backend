echo "TAG_VERSION = $TAG_VERSION"

docker build -t gy-mall-backend:$TAG_VERSION .
docker tag gy-mall-backend:$TAG_VERSION ccr.ccs.tencentyun.com/aweffr-main/gy-mall-backend:$TAG_VERSION
docker push ccr.ccs.tencentyun.com/aweffr-main/gy-mall-backend:$TAG_VERSION
