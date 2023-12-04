
import asyncio
from gui import Gui
from manager_service import ManagerService

        
async def main():
    manager = ManagerService()
    Gui(manager).menu()

if __name__ == "__main__":
    asyncio.run(main())