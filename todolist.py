from typing import List


def todolist() -> None:
    todo: List[str] = ['Do yoga', 'Make breakfast', 'Learn basics of SQL', 'Learn what is ORM']
    print("Today:", *(f"{num}) {task}" for num, task in enumerate(todo, 1)), sep='\n')


if __name__ == '__main__':
    todolist()
