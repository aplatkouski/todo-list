from datetime import date, datetime
from typing import Any, Callable, Dict, NoReturn, Tuple

from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Choice = Tuple[str, Callable[..., Any]]
MenuOptions = Dict[str, Choice]

db_name: str = "todo.db"
engine = create_engine(f'sqlite:///{db_name}?check_same_thread=False', echo=False)
session_factory = sessionmaker(bind=engine)
SqliteSession = scoped_session(session_factory)

Base = declarative_base()


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __init__(self, task: str, deadline: date = datetime.today().date()) -> None:
        self.task = task
        self.deadline = deadline

    def __str__(self) -> str:
        assert self.task
        return self.task

    def __repr__(self) -> str:
        return (
            f"<Task(id='{self.id}', "
            f"task={self.task}, "
            f"deadline={self.deadline})>"
        )


class ToDoList:
    def __init__(self, session: Any) -> None:
        self._session = session
        self.menu_options: MenuOptions = {
            '1': ("Today's tasks", self.print_tasks),
            '2': ("Add task", self.add_task),
            '0': ("Exit", self._exit),
        }

    @staticmethod
    def _make_choice(options: MenuOptions) -> Choice:
        print(*(f"{num}) {value[0]}" for num, value in options.items()), sep='\n')
        option: str = ''
        while option not in options:
            option = input()
        return options[option]

    @staticmethod
    def _exit() -> NoReturn:
        print("\nBye!")
        exit()

    def print_tasks(self, deadline: date = datetime.today().date()) -> None:
        print("\nToday:")
        tasks = (
            self._session.query(Task)
            .filter(Task.deadline == deadline)
            .order_by(Task.id)
            .all()
        )
        if tasks:
            print(
                *(f"{num}. {task}" for num, task in enumerate(tasks, start=1)), sep='\n'
            )
        else:
            print("Nothing to do!")
        print("\n")

    def add_task(self) -> None:
        task: str = input("\nEnter task\n")
        self._session.add(Task(task))
        self._session.commit()
        print("The task has been added!\n")

    def cli(self) -> None:
        while True:
            choice: Choice = self._make_choice(self.menu_options)
            choice[1]()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    todo_list: ToDoList = ToDoList(session=SqliteSession())
    todo_list.cli()
