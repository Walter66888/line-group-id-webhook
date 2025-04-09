from flask import Flask, request, abort
import os
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 取得LINE API密鑰
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_TOKEN')

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/", methods=['GET'])
def home():
    return "Webhook server is running!"

@app.route("/webhook", methods=['POST'])
def callback():
    # 獲取X-Line-Signature頭部值
    signature = request.headers['X-Line-Signature']

    # 獲取請求體
    body = request.get_data(as_text=True)
    logger.info("Request body: %s", body)

    try:
        # 驗證簽名
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 這裡將捕獲所有訊息事件
    message_type = event.source.type
    
    if message_type == 'group':
        group_id = event.source.group_id
        logger.info(f"捕獲到群組ID: {group_id}")
        
        # 可選：回覆確認訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=f"已捕獲群組ID: {group_id}\n請在您的應用中使用此ID")
        )
    elif message_type == 'room':
        room_id = event.source.room_id
        logger.info(f"捕獲到聊天室ID: {room_id}")
    else:
        user_id = event.source.user_id
        logger.info(f"捕獲到用戶ID: {user_id}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
