import asyncio
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from manager_service import ManagerService

    
class Gui:    
    def __init__(self, manager: ManagerService):
        self.console = Console()
        self.manager = manager
    
    async def menu(self):
        while True:            
            self._display()
            self.console.print("1) Criar\n2) Selecionar\n3) Atualizar\n4) Sair")
            choice = await asyncio.to_thread(input)
            if choice == '1':
                self._display()
                self.console.print("Criar sessão")
                while True:
                    name = Prompt.ask("Nome")
                    if name is not None and name.isalnum():
                        break
                self.manager.create_session(name)
            elif choice == '2':
                self._display()
                while True:
                    choice = await asyncio.to_thread(input)
                    if choice.isnumeric() and int(choice) - 1 < len(self.manager.sessions):
                        break               
                session = int(choice)-1
                self._display(int(choice)-1)
                self.console.print("1) Iniciar\n2) Voltar")
                while True:
                    choice = await asyncio.to_thread(input)                  
                    if choice == '1':
                        asyncio.create_task(self.manager.sessions[session].run())
                        self.console.clear()
                        print("Iniciando...")
                        break
            elif choice == '3':
                pass
            elif choice == '4':
                self._display()
                self.console.print("Sair?")
                self.console.print("1) Sim\n2) Não")
                choice = await asyncio.to_thread(input)
                if choice == '1':
                    quit()
            else:
                pass
            
    def _display(self, highlight = None):
        self.console.clear()
        table = Table(show_header=True, show_lines=True, header_style="bold cyan")
        table.add_column("", style="dim", min_width=2)
        table.add_column("Session", width=20)
        table.add_column("Running", min_width=6)
        table.add_column("Logged In", min_width=6)
        for i in range(len(self.manager.sessions)):
            session = self.manager.sessions[i]
            if highlight is not None and i == highlight:
                table.add_row(f"[bold purple]{str(i+1)}", f"[bold purple]{session.name}", f"[bold purple]{str(session.running)}", f"[bold purple]{str(session.logged_in)}")
            else:
                table.add_row(str(i+1), session.name, str(session.running), str(session.logged_in))
        self.console.print(table)