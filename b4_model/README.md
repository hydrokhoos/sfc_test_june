# B4 Model

コンテナ準備 (リレーサービス1個)
```bash
# ./create.sh <num_services>
./create.sh 1
```

コンテンツ取得
```bash
docker exec consumer sh -c "ndncatchunks /relay1/img.jpg -f > /fetched.jpg"
```

コンテナ削除 (リレーサービス1個)
```bash
# ./delete.sh <num_services>
./delete.sh 1
```
