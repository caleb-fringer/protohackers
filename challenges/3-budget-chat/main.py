import asyncio
from functools import partial


type ConnectedUsers = dict[str, asyncio.StreamWriter]

async def request_username(
    reader: asyncio.StreamReader, 
    writer: asyncio.StreamWriter
) -> str:
    '''
    Request username from user & read their response.
    Decodes, strips, and returns the result w/o validating.
    '''
    message = "Welcome to budgetchat! What shall I call you?\n"
    writer.write(message.encode(encoding="ascii"))
    await writer.drain()

    data = await reader.readline()
    message = data.decode(encoding="ascii")
    username = message.strip()
    return username

def is_valid(username: str) -> bool:
    '''
    Checks if a given username is valid according to the protocol rules.
    Does not check for duplicates.
    '''
    if len(username) < 1:
        return False
    return username.isalnum()

def is_unique(username: str, users: ConnectedUsers) -> bool:
    '''
    Checks if the given username is unique among the connected users
    '''
    return username not in users

def get_peers(username: str, users: ConnectedUsers) -> list[str]:
    return [peer for peer in users if peer != username]

async def greet_user(
    users: ConnectedUsers,
    user: str,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> None:
    '''
    Send a greeting to the newly connected user w/ a list of all the peers
    who are connected to the chat room.
    '''
    peers = [peer for peer in users if peer != user]
    message = f"* The room contains: {", ".join(users)}\n"
    writer.write(message.encode(encoding="ascii"))
    await writer.drain()

async def unicast(
    users: ConnectedUsers,
    sender: str,
    receiver: str,
    message: str
):
    '''
    Given a list of users, the sender's username, the receiver's username, and
    a message, broadcast the message to all connected peers.
    '''
    users[receiver].write(message.encode(encoding="ascii"))
    await users[receiver].drain()

async def broadcast(
    users: ConnectedUsers,
    sender: str,
    message: str
) -> None:
    '''
    Given a list of users, the sender's username, and a message, broadcast
    the message to all connected peers.
    '''
    recipients = [peer for peer in users if peer != sender]
    await asyncio.gather(
        *[unicast(users, sender, receiver, message) for receiver in recipients]
    )

async def handle_login(
    users: ConnectedUsers,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> str:
    '''
    Handles the entire login process:
    - Request a username
    - Validate username
    - Check for duplicate user

    Loops until a valid, unique username is input. 
    Returns the username when successful.
    Side effect: Adds username to users.
    '''
    username: str = ""
    while not (is_valid(username) and is_unique(username, users)):
        print("Prompting username...")
        username = await request_username(reader, writer)

    print(f"{username} has connected.")
    # Add user to users group
    users[username] = writer

    return username

def format_message(sender: str, message: str) -> str:
    return f"[{sender}] {message}"

async def handle_connection(
        users: ConnectedUsers, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
) -> None:
    '''
    - Request username
    - Validate username
    - Check for duplicate user
    - Welcome user & broadcast to others
    Until the user disconnects:
      - If a message comes in from the user, broadcast it
      - If a message comes in from another user, deliver it
    Then,
        - Remove user from usermap
        - Broadcast disconnection   
    '''
    peername = writer.get_extra_info("peername")
    print(f"Connection received from {peername}")

    # Handle the whole login flow.
    try:
        username = await handle_login(users, reader, writer)
    except ConnectionError:
        print(f"Peer at {peername} disconnected!")
        return
    except Exception as e:
        print(f"An unexpected exception occured while logging in user: {e}")
        return
    
    print(f"{username} has logged in!")

    try:
        await asyncio.gather(
            # Greet the user before modifying users map, 
            # since it broadcasts to the entire user group
            greet_user(users, username, reader, writer),
            # Announce membership change
            broadcast(users, username, f"* {username} has entered the room\n")
        )
        
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode(encoding="ascii")
            if message.strip() == "q":
                break
            print(f"Received message from {username}")
            await broadcast(users, username, format_message(username, message))

    except ConnectionError:
        print(f"Peer at {peername} disconnected!")
        return
    except Exception as e:
        print(f"An unexpected exception occured: {e}")
        return
    finally:
        print(f"Disconnecting {username}")
        users.pop(username, None)
        await broadcast(users, username, f"* {username} has left the room\n")

    
async def main(address:str="0.0.0.0", port:int=8080) -> None:
    users: ConnectedUsers = {}
    try:
        server = await asyncio.start_server(
            partial(handle_connection, users), 
            address, 
            port
        )
        print(f'Serving on port {port}...')
    except Exception as e:
        print(f"Error starting server: {e}")
        return

    async with server:
        await server.serve_forever()

        
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nShutting down gracefully...")
