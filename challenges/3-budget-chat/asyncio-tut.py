'''
Demos from https://www.youtube.com/watch?v=-CzqsgaXUM8&list=PLhNSoGM2ik6SIkVGXWBwerucXjgP1rHmB&index=3
'''
import asyncio
from datetime import datetime


def print_now():
    print(datetime.now())

async def keep_printing(name: str = ""):
    while True:
        print(name, end=" ")
        print_now()
        try:
            await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print(f"{name} was cancelled")
            break

async def async_main(name):
    '''
    Async functions RETURN coroutines, which are just awaitable objects.
    '''
    kp = keep_printing(name)
    waiter = asyncio.wait_for(kp, 2)
    try:
        await waiter
    except (asyncio.TimeoutError, KeyboardInterrupt):
        '''
        KeyboardInterrupt is not caught here becase of cancellation/propagation
        '''
        print("Time's up!")

asyncio.run(async_main("Main"))

async def async_main_serial():
    '''
    Because these are executed as coroutines (NOT tasks), each await is
    serially executed.
    '''
    cos = ["First", "Second", "Third"]
    for co in cos:
        try:
            await asyncio.wait_for(keep_printing(f"{co} (serial)"), 2)
        except asyncio.TimeoutError:
            print("Time's up!")
    
asyncio.run(async_main_serial())

async def async_main_parallel():
    '''
    Using gather, however, will execute them in parallel.
    '''
    try:
        await asyncio.wait_for(
                asyncio.gather(
                    keep_printing("First (parallel)"),
                    keep_printing("Second (parallel)"),
                    keep_printing("Third (parallel)"),
                ),
                2,
        )
    except asyncio.TimeoutError:
        print("Time's up!")

asyncio.run(async_main_parallel())
