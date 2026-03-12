a = 10
b = 5

import json
import math


def f(x, y):
    return x + y


class UserManager:
    def __init__(self, users: list):
        self.users = users

    def add_user(self, user):
        self.users.append(user)

    def print_all_users(self):
        for u in self.users:
            print(u)

    def calculate_sum(self, a, b):
        return a + b


def divide(a, b):
    return a / b


def divide_safely(a, b):
    if b == 0:
        return None
    return a / b


if False:
    print("Never happens")

if a == 10:
    print("A is 10")
