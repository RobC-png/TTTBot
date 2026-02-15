import discord
from discord.ext import commands
import os  # for the token, which is in another file
from random import randint
from time import sleep

# Read token from token.txt
def get_token():
    with open("token.txt", "r") as f:
        return f.read().strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


playersTurn = True
Move_is_Viable = False
game_is_running = False
gameWon = False
kästchen = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]
Winner = "-"
current_channel = None


# EmojyTranslator must be defined before board_str
def EmojyTranslator(text):
    if text == "-":
        return ":white_large_square:"
    if text == "X":
        return ":x:"
    if text == "O":
        return ":blue_circle:"

# Helper to display the board as a string
def board_str():
    return (f"{EmojyTranslator(kästchen[0])} {EmojyTranslator(kästchen[1])} {EmojyTranslator(kästchen[2])}\n"
            f"{EmojyTranslator(kästchen[3])} {EmojyTranslator(kästchen[4])} {EmojyTranslator(kästchen[5])}\n"
            f"{EmojyTranslator(kästchen[6])} {EmojyTranslator(kästchen[7])} {EmojyTranslator(kästchen[8])}")

# Discord bot commands
@bot.command()
async def ttt(ctx):
    global game_is_running, playersTurn, kästchen, Winner, gameWon, current_channel
    if game_is_running:
        await ctx.send("A game is already running!")
        return
    game_is_running = True
    playersTurn = True
    kästchen = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]
    Winner = "-"
    gameWon = False
    current_channel = ctx.channel
    await ctx.send("Tic-Tac-Toe started! Use !move <1-9> to play.\n" + board_str())

@bot.command()
async def move(ctx, pos: int):
    global playersTurn, kästchen, gameWon, game_is_running
    if not game_is_running:
        await ctx.send("No game running. Start with !ttt")
        return
    if not playersTurn:
        await ctx.send("It's not your turn!")
        return
    if pos < 1 or pos > 9:
        await ctx.send("Invalid move. Use 1-9.")
        return
    idx = pos - 1
    if not emtpyCheck(idx):
        await ctx.send("That spot is already taken!")
        return
    PlayerInput(idx)
    await ctx.send("You moved:\n" + board_str())
    # Check win/draw
    result = Wincheck(kästchen)
    if result == "X":
        await ctx.send("You win!")
        Fin("X")
        return
    elif result == "draw":
        await ctx.send("Draw!")
        Fin("-")
        return
    # Computer turn
    playersTurn = False
    ComputerTurn(kästchen)
    await ctx.send("Computer moved:\n" + board_str())
    result = Wincheck(kästchen)
    if result == "O":
        await ctx.send("Computer wins!")
        Fin("O")
        return
    elif result == "draw":
        await ctx.send("Draw!")
        Fin("-")
        return
    playersTurn = True


def emtpyCheck(k):
    if kästchen[k] != "-":
        return False
    else:
        return True

#Überschreibt eine Zelle im Grid
def overwriting(k, zeichen, liste):
    liste[k] = zeichen

#PlayerTurn
def PlayerInput(k):
    overwriting(k, "X", kästchen)

def Wincheck(kästchen):
    #1. Reihe
    if kästchen[0] == kästchen[1] == kästchen[2] and kästchen[0] != "-":
        return f"{kästchen[0]}"

    #2. Reihe
    if kästchen[3] == kästchen[4] == kästchen[5] and kästchen[3] != "-":
        return f"{kästchen[3]}"

    #3. Reihe
    if kästchen[6] == kästchen[7] == kästchen[8] and kästchen[6] != "-":
        return f"{kästchen[6]}"

    #1. Spalte
    if kästchen[0] == kästchen[3] == kästchen[6] and kästchen[0] != "-":
        return f"{kästchen[0]}"

    #2. Spalte
    if kästchen[1] == kästchen[4] == kästchen[7] and kästchen[1] != "-":
        return f"{kästchen[1]}"

    #3. Spalte
    if kästchen[2] == kästchen[5] == kästchen[8] and kästchen[2] != "-":
        return f"{kästchen[2]}"

    #LORU Diagonal
    if kästchen[0] == kästchen[4] == kästchen[8] and kästchen[0] != "-":
        return f"{kästchen[0]}"

    #ROLU Diagonal
    if kästchen[2] == kästchen[4] == kästchen[6] and kästchen[2] != "-":
        return f"{kästchen[2]}"
    
    #Draw
    if kästchen[0] != "-" and kästchen[1] != "-" and kästchen[2] != "-" and kästchen[3] != "-" and kästchen[4] != "-" and kästchen[5] != "-" and kästchen[6] != "-" and kästchen[7] != "-" and kästchen[8] != "-":
        return "draw"

    else:
        return "nothing"


#ComputerTurn
def ComputerTurn(Spielfeld):
    global kästchen

    #Computer "AI"
    Move_is_Viable = False
    #Macht eine Liste aller verfügbaren Moves
    available_Moves = []
    for i in range(9):
        if kästchen[i] == "-":
            available_Moves.append(i)
    
    #Erstellt Listen um die Moves einzuordnen
    O_wins = []
    other_outcomes = []

    #Checkt ob die Moves "Gut" sind
    #Loopt über alle Möglichen Moves
    for i in range(len(available_Moves)):
        #Ertsellt eine Kopie des Jetzigen Spielfelds (FIXED: now creates actual copy)
        field_temp = kästchen.copy()

        #Tragt den möglichen Move in das kopierte Spielfeld ein
        overwriting(available_Moves[i], "O", field_temp)

        #Checkt ob der Move einen Win als Resultat hat
        if Wincheck(field_temp) == "O":
            #Wenn ja fügt es den Move zu den Moves hinzu, die zu einem Win führen
            O_wins.append(available_Moves[i])
        else:
            #Wenn nicht fügt es den Move zu allen anderen Moves hinzu
            other_outcomes.append(available_Moves[i])

    #Picked 1 Option der Liste (nice)
    if len(O_wins) > 0:
        pick = O_wins[randint(0, len(O_wins) - 1)]
    else:
        pick = other_outcomes[randint(0, len(other_outcomes) - 1)]
    
    #Überschreibt das gepickte Feld mit "O"
    overwriting(pick, "O", kästchen)

def Fin(Winner_):
    global Winner
    Winner = Winner_
    global kästchen
    kästchen = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]
    global game_is_running
    game_is_running = False
    global gameWon
    gameWon = True


# Run the bot
if __name__ == "__main__":
    token = get_token()
    bot.run(token)