# Agent Model
コンテナ準備
```bash
./create.sh
docker exec -d router1 python3 /src/nfd_api.py
```

リレーサービス追加 (relay1コンテナ作成)
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
docker rm -f producer router1 consumer relay1
docker network rm net1
```
