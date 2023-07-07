# B4 on Router Model

コンテナ準備
```bash
./create.sh
```

リレーサービス追加 (relay1)
```bash
# ./start_relay.sh <relay_number>
./start_relay.sh 1
```

コンテンツ取得
```bash
docker exec consumer sh -c "ndncatchunks /relay1/img.jpg -f > /fetched.jpg"
```

コンテナ削除
```bash
docker rm -f producer router1 consumer
cd ./relay1 && docker-compose down -v && cd .. && rm -r relay1
```
