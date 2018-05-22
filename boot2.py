# from networking.client import NetClient
from models.player import Player


# net = NetClient("127.0.0.1", 2004)
# print("Net initialized...")
print("Welcome player. Please login first:")
usr = input("Username:")
pwd = input("Password:")
player = Player(usr, pwd)
if not player.logged_in:
    print("Unable to login! Bad username/password?")
    q = input("Do you want to register? (y/n)")
    if q.lower().startswith("y"):
        confirm_pwd = input("Confirm your password:")
        reg = player.register(confirm_pwd)
        if reg == "username_taken":
            print(f"The username {usr} is already taken!")
            exit()
        elif reg == "invalid_password":
            print("Password didn't match the confirmed password.")
            exit()
        else:
            print("Registration succesful! You are now logged in.")
else:
    print("Login succesful")

games = player.current_games
print(f"Currently you have {len(games)} active games.")
if len(games) == 0:
    q = input("Do you want to queue for a game? (y/n)")
    if q.lower().startswith("y"):
        player.net.queue_up_new_game()
