__author__ = 'Travis Brackus'
__name__ = 'login'
'''
This module contains the main command prompt for the password vault.
'''

import os
import csv
import pandas as pd
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
    def from_scratch(cls, name, user, url, n, sp):
        cls.n = n
        y1, y2 = cls.random_y(), cls.random_y()
        return cls(name, user, url, y1, y2, n, sp)

    # Calculates random y key
    @classmethod
    def random_y(cls):
        return int(random.uniform(0, 1) * (10 ** cls.n))

    def __init__(self, name, user, url, y1, y2, n, sp):
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


# Returns accounts dataframe
def df_accounts() -> pd.DataFrame:
    return pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'accounts.csv'), index_col = 'NAME')


# Writes account to csv file
def update_csv(acct: account) -> None:
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'accounts.csv')
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
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

    with open(file_path, 'w', newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
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
def display_accounts(df_accts: pd.DataFrame) -> None:
    print('Available Accounts:')
    for n in df_accts.index.tolist():
        print(f'\t{n}')
    pass


# Displays account properties
def display_properties(acct: account) -> None:
    print('Available properties:')
    for key, value in acct.__dict__.items():
        print(f'\t{key}:  {value}')
    pass


# Selects account
def sel_acct() -> account:
    df_accts = df_accounts()
    while True:
        display_accounts(df_accts)
        a = input('Enter account name >>> ').lower()
        if a in df_accts.index.values:
            break
        input('Error accessing account.  Press any key to continue...')
    df_acct = df_accts.loc[a]
    return account(a, df_acct.USER, df_acct.URL, df_acct.Y1, df_acct.Y2, df_acct.N, df_acct.SP)


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
    accts = [i.lower() for i in df_accounts().index.to_list()]
    if acct in accts:
        raise AccountExistsError
    return


# Creates new account
def new_acct() -> None:
    restart = True
    while restart:
        input_msg = ('Please input comma-separated account name, user, url, n, and sp values for the new account >>>')
        acct_params = input(input_msg).replace(' ', '').split(',')

        # validate inputs
        try:
            assert len(acct_params) == 5
            acct_params[-2] = int(acct_params[-2])
            check_account_exists(acct_params[0].lower())
            acct = account.from_scratch(*acct_params)
        except AssertionError:
            print(f'Error: 5 parameters expected, {len(acct_params)} received. Account cannot be created.')
            restart = True
        except ValueError:
            print('Error: Non-numeric value passed as N parameter. Account cannot be created.')
            restart = True
        except AccountExistsError:
            print(f'Error: Account <{acct_params[0]}> already exists.')
            restart = True
            # TODO add optional call to del_acct if user wants to replace
            # existing account
        else:
            restart = False
    
    update_csv(acct)
    input(f'New account <{acct_params[0]}> successfully added.  Press any key to continue...')
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
    # TODO:  code for delete account
    input('Under construction.  Press any key to continue...')
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