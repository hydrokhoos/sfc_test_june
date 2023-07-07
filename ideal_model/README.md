# Ideal Model

コンテナ準備
```bash
./create.sh
```

リレーサービス追加
```bash
cd relay1
docker-compose up -d
```

コンテンツ取得
```bash
docker exec consumer sh -c "ndncatchunks /relay1/img.jpg -f > /fetched.jpg"
```

コンテナ削除
```bash
cd relay1 && docker-compose down -v && cd ..
./delete.sh
```
