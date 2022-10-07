# Medal.tv discord embed fixer bot

You know how medal embeds recently changed to not play the video anymore? and you have to go and click the link to see the clip? well no more, this simple bot retrieves the source video from medal's servers and displays it on discord as God intended.

## Deployment

```
docker build . -t medal-fixer
docker run -d medal-fixer
```