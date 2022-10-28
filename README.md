# Medal.tv discord embed fixer bot

You know how medal embeds recently changed to not play the video anymore? and you have to go and click the link to see the clip? well no more, this simple bot retrieves the source video from medal's servers and displays it on discord as God intended.

[[Add to Server]](https://discord.com/api/oauth2/authorize?client_id=1026513548874096661&permissions=59392&scope=bot)

## Deployment

```
docker build . -t medal-fixer
docker run -d medal-fixer
```

## Usage as a script

Run the bot
```
python main.py
```

Get single medal clip's source
```
python main.py get https://medal.tv/...
```