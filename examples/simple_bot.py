




if __name__ == "__main__":

    client = LoveBotClient()
    client.connect()

    bot = client.create_bot("hugo")

    while True:
        bot.set_wheel_speed(1, 2)

