# Instructions
## Setup and Authentication
### User Id
If you don't know your Twitch User Id, you can use the script in `UserIdTool/user_id_req.py`. This is a Python script (tested only on Python 3+) making use of the `requests` library. The steps to use it are:
1. Install the `requests` library by running `pip install requests`
2. Open the script and replace the value of the `USERNAME` variable with your Twitch username.
3. Run the script with your latest python version, i.e. `python user_id_req.py`
The output should be your Twitch User Id
### OAuth Token
To listen for redeem events you need to authorize the tool via an OAuth token. The steps to do this are:
1. Go to https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=op2ffge97zlikpfm8ss3hzci6kxsip&redirect_uri=http://localhost&scope=channel:read:redemptions
2. Login if necessary and authorize the application
3. You will be redirected to localhost, which will show up as "This site can't be reached" or similar.
4. Look at the address bar of your browser. It should look similar to
`http://localhost/#access_token=XXXXXXXXXXXXXXXXXXXXX&scope=channel%3Aread%3Aredemptions&token_type=bearer`
5. Copy the value associated with "access_token" - this is your OAuth token.
### Load Script
Finally, add both the User Id and the OAuth Token to the script via the UI provided in the scripts page of Streamlabs Chatbot

## Usage
The class `RedeemHandler` in `redeem_detection_StreamlabsSystem.py` is your main entry point. The function `on_event` is called upon any event being detected. Further instructions are available in default the pythondoc of the function.

The method used is listening to a pubsub topic provided by Twitch API. In particular the `channel-points-channel-v1` topic. For more information and examples see https://dev.twitch.tv/docs/pubsub

# Security Considerations
- Your User Id is public, so there are no security concerns regarding giving it to the app.
- The OAuth token is explicitly for listening to Twitch Points redeem events, as you can see upon authorization. It doesn't grant the app any other access.
- The unusual way of obtaining the OAuth token through the address bar is just a result of lack of Web UI (I don't have the time to build one). The '#' in the address bar before the values indicates those are stored as fragments, i.e. they stay in your browser and aren't sent with any HTTP request. Thus there are no concerns that the OAuth token can be stolen.
