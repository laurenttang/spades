# spades
final edition of project spades

自己開 t2.large  16g ram EC2 ->

git clone 程式碼 -> 

安裝 docker / docker-compose ->

docker-compose up -d -> 

把s3資料依照Framework放入 -> (mysql資料整包倒入後 要重新 docker-compose up) 

curl $(docker port chatbot_ngrok 4040)/api/tunnels ->

把 網域 貼到 line Developer , botapp.py ->

(line Develop user/secretkey 更新到botapp.py) ->

開兩個 terminal : docker exec -it jupyter bash ->

1  bash install.sh / bash py.sh 

2  docker exec -it jupyter bash  -> bash bot.sh

這樣就可以還原作品惹 ～
