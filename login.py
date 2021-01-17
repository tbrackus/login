__author__ = 'Travis Brackus'
__name__ = 'login'
'''
This module contains the main command prompt for the password vault.
'''

import os
import csv
import hashlib
import random
import getpass
import pyperclip
import webbrowser


# account class
class account:

    # alternate constructor if account is being created
    # for the first time without y-values
    @classmethod
    def from_scratch(cls, name, user, url, n, sp=''):
        n = int(n)
        cls.n = n  # TODO:  Not sure what this row does.  Shouldn't the 'n' be unique to each account?  What if one account supplier allows 12 max characters, and another allows 16?
        # TODO:  verify that setting both y1 and y2 in one line avoid keys that are close to one another?
        y1, y2 = cls.random_y(), cls.random_y()
        delattr(account, 'n')  # seems prudent to remove the class attr
        return cls(name, user, url, y1, y2, n, sp)

    # Calculates random y key
    @classmethod
    def random_y(cls):
        return int(random.uniform(0, 1) * (10 ** cls.n))

    def __init__(self, name, user, url, y1, y2, n, sp=''):
        self.name = name
        self.user = user
        self.url = url
        self.y1 = y1
        self.y2 = y2
        self.n = n
        self.sp = sp


    # Calculates account key
    def key(self, x1, x2):
        return self.y1 - (self.y2 - self.y1) / (x2 - x1) * x1


    # Returns hashword
    def hashword(self, x1, x2):
        k = str(int(self.key(x1, x2) * (10 ** self.n)))
        s = str(hashlib.sha256(k.encode("utf-8")).digest())
        return s[len(s) - self.n: len(s)] + self.sp


class AccountExistsError(Exception):
    pass


# Returns csv file path
def file_path() -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'accounts.csv')


def read_csv_as_list() -> list:
    with open(file_path(), 'r') as file:
        reader = csv.reader(file)
        return list(reader)


def write_list_to_csv(data: list) -> None:
    with open(file_path(), 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(sorted(data[0:]))
        return


# Writes account to csv file
def update_csv(acct: account) -> None:
    rows = read_csv_as_list()
    row = [str(i) for i in acct.__dict__.values()]

    # Determine if new line needs to be written, otherwise update line
    newfile = True
    for i in range(len(rows)):
        if rows[i][0] == acct.name:
            rows[i] = row
            newfile = False
            break
    if newfile:
        rows.append(row)

    write_list_to_csv(rows)
    return


# Gets key from user
def get_key(txt: str) -> int:
    while True:
        key = getpass.getpass(f'Enter {txt} >>> ')
        if key.isnumeric():
            break
        else:
            print(f'Error.  {txt} must be numeric.')
    return int(key)


# Gets account hashword
def get_hw(acct: account) -> str:
    x1 = get_key('x1 key')
    x2 = get_key('x2 key')
    return acct.hashword(int(x1), int(x2))


# Displays available accounts
def display_accounts(accts: list) -> None:
    print('Available Accounts:')
    for a in accts[1:]:
        print(f'\t{a[0]}')
    pass


# Displays account properties
def display_properties(acct: account) -> None:
    print('Available properties:')
    for key, value in acct.__dict__.items():
        print(f'\t{key}:  {value}')
    pass


# Selects account
def sel_acct() -> account:
    accts = read_csv_as_list()
    restart = True
    while restart:
        display_accounts(accts)
        a = input('Enter account name >>> ').lower()
        for i in range(len(accts)):
            if accts[i][0] == a:
                restart = False
                break
        if restart:
            input('Error accessing account.  Press any key to continue...')
    return account(accts[i][0], accts[i][1], accts[i][2], int(accts[i][3]), int(accts[i][4]), int(accts[i][5]), accts[i][6])


# Gets account info
def get_acct() -> None:
    print('Getting Account Info...')
    acct = sel_acct()
    webbrowser.open_new_tab(acct.url)
    print(f'URL for <{acct.name}> is: {acct.url}')
    pyperclip.copy(acct.user)
    print(f'Username for <{acct.name}> ({acct.user}) has been copied to the clipboard.')
    input('Press any key to continue...')
    hw = get_hw(acct)
    pyperclip.copy(hw)
    print(f'Password for <{acct.name}> has been copied to the clipboard.')
    input('Press any key to continue...')
    return


# Checks to see if account exists
def check_account_exists(acct: str) -> None:
    accts = [i[0] for i in read_csv_as_list()]
    if acct in accts:
        raise AccountExistsError
    return


# Creates new account
def new_acct() -> None:
    restart = True
    msg = 'Press any key to continue...'
    while restart:
        input_msg = ('Enter comma-separated account name, user, url, n, and optional sp values for the new account >>>')
        acct_params = input(input_msg).replace(' ', '').split(',')
        name = acct_params[0]
        try:
            acct = account.from_scratch(*acct_params)
            check_account_exists(name)
        except (TypeError, ValueError):
            input(f'Bad account parameter input. {msg}')
        except AccountExistsError:
            print(f'Account <{name}> already exists. {msg}')
            return
        else:
            restart = False
    update_csv(acct)
    input(f'New account <{name}> successfully added. {msg}')
    return


# Modifies existing account
def mod_acct() -> None:
    print('Modify Existing Account...')
    acct = sel_acct()
    while True:
        display_properties(acct)
        a = input('Enter property to modify >>> ').lower()
        if a in acct.__dict__:
            break
        input('Error accessing property.  Press any key to continue...')
    val = input(f'Enter new value for {a} >>> ')
    setattr(acct, a, val)
    update_csv(acct)
    input(f'<{acct.name}> account has been successfully modified.  Press any key to continue...')
    return


# Deletes account
def del_acct() -> None:
    accts = read_csv_as_list()
    msg = 'Press any key to continue...'
    while True:
        display_accounts(accts)
        name = input('Enter account to delete >>> ').lower()
        if name in [i[0] for i in accts]:
            break
        input(f'Error accessing account. {msg}')

    for i in range(len(accts)):
        if accts[i][0] == name:
            break
    confirm = input(f'Are you sure you wish to delete {name} account?  Enter <y> to confirm or any key to cancel.').lower()
    if confirm == 'y':
        del accts[i]
        write_list_to_csv(accts)
        input(f'Account <{name}> successfully deleted. {msg}')
    return


# Main method to clear screen and restart program
def restart(c) -> None:
    if c == 'e':
        os.system('cls')
        return
    funcs = {'g':get_acct, 'n':new_acct, 'm':mod_acct, 'd':del_acct}
    p = funcs.get(c, 'nothing')
    if p != 'nothing':
        funcs[c]()
    os.system('cls')
    restart(cmds())


# Prints commands to screen and asks for input
def cmds() -> None:
    os.system('cls')
    print('\n**********\tWELCOME TO THE LOGIN TOOL!\t**********\n\n')
    print('Available Commands:\n')
    print('\tg\t\tGet Account Info')
    print('\tn\t\tNew Account')
    print('\tm\t\tModify Account')
    print('\td\t\tDelete Account')
    print('\n\te\t\tExits program\n\n')
    return input('\nEnter Command >>> ').lower()


# Runs
restart(cmds())