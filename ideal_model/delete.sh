docker rm -f producer router1 consumer
for ((i=1; i<=5; i++))
do
  rm -r relay$i
done
