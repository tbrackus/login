__author__ = 'Travis Brackus'
__name__ = 'login'
'''
This module contains the main command prompt for the password vault.
'''

import os
import pandas as pd
import hashlib
import random
import getpass
import pyperclip
import webbrowser


# account class
class account:
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


    # Calculates random y key
    def random_y(self):
        return int(random.uniform(0, 1) * (10 ** self.n))


# Returns accounts dataframe
def df_accounts():
    return pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'accounts.csv'), index_col = 'NAME')


# Gets key from user
def get_key(txt):
    while True:
        key = getpass.getpass('Enter ' + txt + ' >>> ')
        if key.isnumeric():
            break
        else:
            print('Error.  ' + txt + ' must be numeric.')
    return int(key)


# Gets account hashword
def get_hw(acct):
    x1 = get_key('x1 key')
    x2 = get_key('x2 key')
    return acct.hashword(int(x1), int(x2))


# Displays available accounts
def display_accounts(df_accts):
    print('Available Accounts:')
    for n in df_accts.index.values.tolist():
        print('\t' + n)
    pass


# Selects account
def sel_acct():
    df_accts = df_accounts()
    while True:
        display_accounts(df_accts)
        a = input('Enter account name >>> ').lower()
        if a in df_accts.index.values:
            break
        input('Error accessing account.  Press any key to continue...')
    acct = df_accts.loc[a]
    return account(a, acct.USER, acct.URL, acct.Y1, acct.Y2, acct.N, acct.SP)


# Gets account info
def get_acct():
    print('Getting Account Info...')
    acct = sel_acct()
    webbrowser.open_new_tab(acct.url)
    print('URL for <' + acct.name + '> is: ' + acct.url)
    pyperclip.copy(acct.user)
    print('Username for <' + acct.name + '> (' + acct.user + ') has been copied to the clipboard.')
    input('Press any key to continue...')
    hw = get_hw(acct)
    pyperclip.copy(hw)
    print('Password for <' + acct.name + '> has been copied to the clipboard.')
    input('Press any key to continue...')
    return


# Creates new account
def new_acct():
    # TODO:  code for new account
    input('Under construction.  Press any key to continue...')
    return


# Modifies existing account
def mod_acct():
    # TODO:  code for modify account
    input('Under construction.  Press any key to continue...')
    return


# Deletes account
def del_acct():
    # TODO:  code for delete account
    input('Under construction.  Press any key to continue...')
    return


# Main method to clear screen and restart program
def restart(c):
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
def cmds():
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