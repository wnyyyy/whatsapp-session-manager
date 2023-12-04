import asyncio
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from manager_service import ManagerService
from enum import Enum, auto

    
class MenuChoice(Enum):
    CREATE = auto()
    SELECT = auto()
    UPDATE = auto()
    EXIT = auto()

class Gui:
    def __init__(self, manager: ManagerService):
        self.console = Console()
        self.manager = manager

    def menu(self):
        while True:
            self._display()
            self.console.print("1) Criar\n2) Selecionar\n3) Atualizar\n4) Sair")
            choice = self._get_menu_choice()
            if choice == MenuChoice.CREATE:
                self._handle_create()
            elif choice == MenuChoice.SELECT:
                self._handle_select()
            elif choice == MenuChoice.UPDATE:
                pass
            elif choice == MenuChoice.EXIT:
                if self._confirm_exit():
                    break

    def _get_menu_choice(self) -> MenuChoice:
        while True:
            choice = input()
            if choice.isdigit() and 1 <= int(choice) <= 4:
                return MenuChoice(int(choice))

    def _handle_create(self):
        self._display()
        self.console.print("Criar sessão")
        while True:
            name = Prompt.ask("Nome")
            if name and name.isalnum():
                self.manager.create_session(name)
                break

    def _handle_select(self):
        self._display()
        while True:
            choice = input()
            if choice.isnumeric() and int(choice) - 1 < len(self.manager.sessions):
                break
        session = int(choice)-1
        self._display(int(choice)-1)
        self.console.print("1) Iniciar\n2) Voltar")
        choice = input()
        if choice == '1':
            self.manager.sessions[session].run()

    def _confirm_exit(self) -> bool:
        self._display()
        self.console.print("Sair?")
        self.console.print("1) Sim\n2) Não")
        choice = input()
        return choice == '1'

    def _display(self, highlight: int = None):
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