curl -X POST \
     -H 'Authorization: Bearer token_here' \
     -H 'Content-type: application/json;charset=utf-8' \
    --data '{"channel":"#general","text":"Hello, Slack!"}' \
https://slack.com/api/chat.postMessage