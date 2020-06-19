from datetime import date, timedelta
from typing import Any, Callable, Dict, List, NoReturn, Tuple

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
    deadline = Column(Date, default=date.today())

    def __init__(self, task: str, deadline: date = date.today()) -> None:
        self.task = task
        self.deadline = deadline

    def __str__(self) -> str:
        assert self.task
        return self.task

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id='{self.id}', "
            f"task={self.task}, "
            f"deadline={self.deadline})>"
        )


class ToDoList:
    def __init__(self, session: Any) -> None:
        self._session = session
        self.menu_options: MenuOptions = {
            '1': ("Today's tasks", self._print_today_tasks),
            '2': ("Week's tasks", self._print_week_tasks),
            '3': ("All tasks", self._print_all_tasks),
            '4': ("Missed tasks", self._print_missed_tasks),
            '5': ("Add task", self.add_task),
            '6': ("Delete task", self._delete_missed_tasks),
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

    @staticmethod
    def _print_tasks(tasks: List['Task'], verbose: bool = False) -> None:
        if tasks:
            print(
                *(
                    f"{num}. {task.task}"
                    f"{'. ' + task.deadline.strftime('%-d %b') if verbose else ''}"
                    for num, task in enumerate(tasks, start=1)
                ),
                sep='\n',
                end='\n\n'
            )
        else:
            print("Nothing to do!\n")

    def _print_today_tasks(self) -> None:
        today = date.today().strftime('%d %b')
        print(f"\nToday {today}:")
        tasks: List['Task'] = (
            self._session.query(Task)
            .filter(Task.deadline == date.today())
            .order_by(Task.id)
            .all()
        )
        self._print_tasks(tasks)

    def _print_week_tasks(self) -> None:
        start_date = date.today()
        end_date = date.today() + timedelta(days=7)
        tasks: List['Task'] = (
            self._session.query(Task)
            .filter(Task.deadline.between(start_date, end_date))
            .order_by(Task.deadline)
            .all()
        )
        date_range = [
            start_date + timedelta(days=day)
            for day in range((end_date - start_date).days)
        ]
        for day in date_range:
            print(day.strftime('%A %-d %b:'))
            self._print_tasks(list(filter(lambda t: t.deadline == day, tasks)))

    def _print_all_tasks(self) -> None:
        print("\nAll tasks:")
        tasks: List['Task'] = self._session.query(Task).order_by(Task.deadline).all()
        self._print_tasks(tasks, verbose=True)

    def _select_missed_tasks(self) -> List['Task']:
        tasks: List['Task'] = (
            self._session.query(Task)
            .filter(Task.deadline < date.today())
            .order_by(Task.deadline)
            .all()
        )
        return tasks

    def _print_missed_tasks(self) -> None:
        print(f"\nMissed tasks:")
        tasks = self._select_missed_tasks()
        if tasks:
            self._print_tasks(tasks, verbose=True)
        else:
            print("Nothing is missed!\n")

    def _delete_missed_tasks(self) -> None:
        tasks: List['Task'] = self._select_missed_tasks()
        if not tasks:
            print("Nothing to delete\n")
            return
        print("\nChose the number of the task you want to delete:")
        self._print_tasks(tasks, verbose=True)

        tasks_dict: Dict[int, 'Task'] = dict(enumerate(tasks, start=1))
        num: int = 0
        while num not in tasks_dict:
            num = int(input())
        self._session.delete(tasks_dict[num])
        self._session.commit()
        print("The task has been deleted!\n")

    def add_task(self) -> None:
        task: str = input("\nEnter task\n")
        deadline: str = input("Enter deadline\n")
        # New in version 3.7.: date.fromisoformat(date_string)
        self._session.add(Task(task=task, deadline=date.fromisoformat(deadline)))
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
