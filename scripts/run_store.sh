export $(cat ./server/.env.dev) 

python ./scripts/store_daily.py