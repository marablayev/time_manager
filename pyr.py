from pyrogram import Client

api_id = 1170376
api_hash = "4279af031caf37b4219032995f7e9dea"

with Client("my_account", api_id, api_hash) as app:
    app.send_message("@dev_time_manager_bot", "Greetings from **Pyrogram**!")
