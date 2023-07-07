# コンテンツ要求間隔
SLEEP_INTERVAL=5
# 要求回数
NUM_REQUESTS=5
# サービス数
NUM_SERVICES=1


: > /fetched.jpg
: > /fetched.txt

for ((i=1; i<=$NUM_REQUESTS; i++))
do
	RAND_SERVICE=relay$(shuf -i 1-$NUM_SERVICES -n 1)
	echo "#$i /$RAND_SERVICE/img.jpg"
	# echo "#$i /relay2/relay1/img.jpg"
	echo "=== #$i /$RAND_SERVICE/img.jpg ===" >> /fetched.txt
	# echo "=== #$i /relay2/relay1/img.jpg ===" >> /fetched.txt
	(time ndncatchunks -f /$RAND_SERVICE/img.jpg 1> /fetched.jpg 2>> /fetched.txt) 2>> /fetched.txt
	# (time ndncatchunks -f /relay2/relay1/img.jpg 1> /fetched.jpg 2>> /fetched.txt) 2>> /fetched.txt
	sleep $SLEEP_INTERVAL
	echo "done"
	echo "==================================" >> /fetched.txt
	echo "" >> /fetched.txt
done
