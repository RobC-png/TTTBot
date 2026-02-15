import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from random import randint

# Read token from token.txt
def get_token():
    with open("token.txt", "r") as f:
        return f.read().strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Game state
class GameState:
    def __init__(self):
        self.board = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]
        self.player_turn = True
        self.game_active = False
        self.message = None
        self.player_id = None

game = GameState()


# No text board needed anymore - buttons show everything!


def check_win(board):
    # Check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] and board[i] != "-":
            return board[i]
    
    # Check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] and board[i] != "-":
            return board[i]
    
    # Check diagonals
    if board[0] == board[4] == board[8] and board[0] != "-":
        return board[0]
    if board[2] == board[4] == board[6] and board[2] != "-":
        return board[2]
    
    # Check draw
    if "-" not in board:
        return "draw"
    
    return None


def computer_move():
    """Simple AI that tries to win, then blocks, then picks random"""
    available = [i for i, x in enumerate(game.board) if x == "-"]
    
    # Try to win
    for move in available:
        test_board = game.board.copy()
        test_board[move] = "O"
        if check_win(test_board) == "O":
            game.board[move] = "O"
            return
    
    # Try to block player
    for move in available:
        test_board = game.board.copy()
        test_board[move] = "X"
        if check_win(test_board) == "X":
            game.board[move] = "O"
            return
    
    # Random move
    move = available[randint(0, len(available) - 1)]
    game.board[move] = "O"


class TicTacToeButton(Button):
    def __init__(self, position):
        self.position = position
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="⬜",
            row=position // 3  # This creates the 3x3 grid layout
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Check if it's the right player
        if interaction.user.id != game.player_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return
        
        # Check if game is active
        if not game.game_active:
            await interaction.response.send_message("No active game!", ephemeral=True)
            return
        
        # Check if it's player's turn
        if not game.player_turn:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return
        
        # Check if position is empty
        if game.board[self.position] != "-":
            await interaction.response.send_message("That spot is taken!", ephemeral=True)
            return
        
        # Make player move
        game.board[self.position] = "X"
        game.player_turn = False
        
        # Update button - Red X
        self.label = "❌"
        self.disabled = True
        self.style = discord.ButtonStyle.danger
        
        # Check if player won
        result = check_win(game.board)
        if result == "X":
            await interaction.response.edit_message(
                content=f"🎉 **You win!**",
                view=self.view
            )
            game.game_active = False
            # Disable all buttons
            for item in self.view.children:
                item.disabled = True
            await interaction.edit_original_response(view=self.view)
            return
        elif result == "draw":
            await interaction.response.edit_message(
                content=f"🤝 **It's a draw!**",
                view=self.view
            )
            game.game_active = False
            for item in self.view.children:
                item.disabled = True
            await interaction.edit_original_response(view=self.view)
            return
        
        # Computer's turn
        await interaction.response.edit_message(
            content=f"💭 Computer is thinking...",
            view=self.view
        )
        
        computer_move()
        game.player_turn = True
        
        # Update view with computer's move
        new_view = TicTacToeView()
        
        result = check_win(game.board)
        if result == "O":
            await interaction.edit_original_response(
                content=f"🤖 **Computer wins!**",
                view=new_view
            )
            game.game_active = False
            for item in new_view.children:
                item.disabled = True
            await interaction.edit_original_response(view=new_view)
            return
        elif result == "draw":
            await interaction.edit_original_response(
                content=f"🤝 **It's a draw!**",
                view=new_view
            )
            game.game_active = False
            for item in new_view.children:
                item.disabled = True
            await interaction.edit_original_response(view=new_view)
            return
        
        await interaction.edit_original_response(
            content=f"Your turn!",
            view=new_view
        )


class TicTacToeView(View):
    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout
        
        # Create 3x3 grid of buttons
        for i in range(9):
            button = TicTacToeButton(i)
            
            # Update button based on board state
            if game.board[i] == "X":
                button.label = "❌"
                button.disabled = True
                button.style = discord.ButtonStyle.danger  # Red
            elif game.board[i] == "O":
                button.label = "🔵"
                button.disabled = True
                button.style = discord.ButtonStyle.primary  # Blue
            
            self.add_item(button)
    
    async def on_timeout(self):
        # Disable all buttons when timeout occurs
        for item in self.children:
            item.disabled = True
        if game.message:
            await game.message.edit(
                content=f"{game.message.content}\n\n⏰ **Game timed out!**",
                view=self
            )


@bot.command()
async def ttt(ctx):
    """Start a new Tic-Tac-Toe game"""
    if game.game_active:
        await ctx.send("A game is already running! Finish it first.")
        return
    
    # Reset game
    game.board = ["-", "-", "-", "-", "-", "-", "-", "-", "-"]
    game.player_turn = True
    game.game_active = True
    game.player_id = ctx.author.id
    
    view = TicTacToeView()
    game.message = await ctx.send(
        f"**Tic-Tac-Toe Started!**\n{ctx.author.mention}, you are ❌. Computer is 🔵. Your turn!",
        view=view
    )


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready to play Tic-Tac-Toe!')


# Run the bot
if __name__ == "__main__":
    token = get_token()
    bot.run(token)