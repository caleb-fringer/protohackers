from libevdev.device import InvalidArgumentException
import asyncio
from functools import partial

def is_valid(username: str) -> bool:
    if len(username) < 1:
        return False
    return username.isalnum()

type ConnectedUsers = dict[str, asyncio.StreamWriter]

async def request_username(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> str:
    pass

    
async def handle_login(
    users: ConnectedUsers,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter
) -> str | None:
    '''
    Handles the entire login process:
    - Request a username
    - Validate username
    - Check for duplicate user
    - On success, add user to users list

    Returns (username, True) if successful, and (None, False) if unsuccessful
    '''
    writer.write("Welcome to budgetchat! What shall I call you?\n".encode(encoding="ascii"))
    await writer.drain()

    data = await reader.readline()
    message = data.decode(encoding="ascii")
    username = message.strip()

    if not is_valid(username):
        writer.write("Invalid username. Usernames must be at least 1 character long and contain only alphanumeric characters\n".encode(encoding="ascii"))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return None

    if username in users:
        writer.write(f"{username} is already connected! Rejecting!\n".encode(encoding="ascii"))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return None

    print(f"{username} has connected.")
    users[username] = writer
    return username

async def handle_connection(
        users: ConnectedUsers, 
        reader: asyncio.StreamReader, 
        writer: asyncio.StreamWriter
) -> None:
    username = await handle_login(users, reader, writer)
    if username is None:
        raise Exception("Login process failed")
     
    # Announce users and welcome incoming user
    writer.write(f"* The room contains: {", ".join(users.keys())}\n".encode(encoding="ascii"))
    for user in filter(lambda user: user != username, users):
        users[user].write(f"* {username} has entered the room\n".encode(encoding="ascii"))

    await asyncio.gather(*(writer.drain() for writer in users.values()))

    # Chat loop
    while True:
        try:
            peers = filter(lambda user: user != username, users)
            data = await reader.readline()
            message = data.decode(encoding="ascii")
            for peer in peers:
                users[peer].write(f"[{username}] {message}\n".encode(encoding="ascii"))
            await asyncio.gather(*(users[peer].drain() for peer in peers))
        except Exception as e:
            print(f"{username}: Failed to deliver message: {e}")
            break

    writer.write("Disconnecting from budgetchat...\n".encode(encoding="ascii"))
    for user in filter(lambda user: user != username, users):
        users[user].write(f"* {username} has left the room\n".encode(encoding="ascii"))
    del users[username]
    await asyncio.gather(*(writer.drain() for writer in users.values()))
    
    print(f"{username} has disconnected.")

    writer.close()
    await writer.wait_closed()

async def main(address:str="127.0.0.1", port:int=8080) -> None:
    users: ConnectedUsers = {}
    server = await asyncio.start_server(
        partial(handle_connection, users), 
        address, 
        port
    )

    print(f'Serving on port {port}...')

    async with server:
        await server.serve_forever()
        
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nShutting down gracefully...")
