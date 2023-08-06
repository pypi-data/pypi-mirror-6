#!/usr/bin/python
# -*- encoding:utf-8 -*-
'''コマンドラインでのパスワードマネージャー
パスワードをpickleで保存する
'''
import hashlib
import cPickle as pickle
from collections import defaultdict
import os
from argparse import ArgumentParser
from random import randint
import subprocess
import getpass

class PasswordManager(object):
    ''' コマンドラインでのパスワードマネージャー '''
    PASS_FILE = '{home}/.pass-manager.db'.format(home=os.environ['HOME'])

    def __init__(self):
        '''PASS_FILEにファイルが無ければ新規作成
        あれば読み込み
        '''
        if os.path.exists(self.PASS_FILE):
            try:
                with open(self.PASS_FILE, 'r') as f:
                    self.passwds = pickle.load(f)
            except Exception, e:
                print '読み込みに失敗', e
                os.remove(self.PASS_FILE)
                raise Exception('再度実行して下さい')
            master = self.passwds['master']
        else:
            self.passwds = defaultdict(str)
            master = getpass.getpass('まずマスターパスワードを決定して下さい => ')
            self.passwds['master'] = master
            self._save_db()

        # マスターパスワードをセットする
        self.sha = hashlib.sha256(master)

    def _save_db(self):
        '''PASS_FILEを保存・更新する
        '''
        try:
            with open(self.PASS_FILE, 'w') as f:
                pickle.dump(self.passwds, f)
        except Exception as e:
            raise Exception('保存出来ませんでした:{0}'.format(e=e))

    def setpb_data(self, data):
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        p.communicate(data)


    def passwd_generator(self, salt):
        '''新しくパスワードを生成する
        '''
        self.sha.update(salt)
        digest = self.sha.hexdigest()[-12:]
        return self.passwd_strengthen(digest)

    def passwd_strengthen(self, digest):
        strengthened_digest = []
        for c in digest:
            if c.isalpha() and randint(1, 10) % 2:
                c = c.upper()
            strengthened_digest.append(c)
        return ''.join(strengthened_digest)

    def save_passwd(self, salt, passwd):
        '''saltをキーとしてpasswdを保存する
        '''
        if self.passwds.has_key(salt):
            to_overwrite = ""
            while to_overwrite not in ['y', 'n']:
                to_overwrite = raw_input('上書きしますか？(y or n)')
            if to_overwrite == 'n':
                return False
        self.passwds[salt] = passwd
        self._save_db()
        return True

    def confirm_master(self):
        '''現在のマスターパスワードで認証を行う
        '''
        valid_master = getpass.getpass(\
                '現在のマスターパスワードを入力して下さい => ')
        if valid_master == self.passwds['master']:
            return True
        else:
            return False

    def show_passwds(self):
        '''生成済みのパスワード一覧を表示する
        '''
        valid_master = self.confirm_master()
        if valid_master:
            if len(self.passwds) == 1:
                print '何もありません'
                return
            for k, v in self.passwds.iteritems():
                if k == 'master':
                    continue
                print '{k}: {v}'.format(k=k, v=v)
        else:
            print '間違っています...'


    def create_passwd(self):
        '''新しくパスワードを生成する
        '''
        salt = raw_input(\
                'パスワードに対するキーワード(ドメイン名など)を入力して下さい => ')
        while salt is 'master':
            print '"master"は利用できません'
            salt = raw_input('再度、キーワードを入力して下さい => ')
        passwd = self.passwd_generator(salt)
        is_updated = self.save_passwd(salt, passwd)
        passwd = passwd if is_updated else self.passwds[salt]
        # print 'パスワードはこちらです\n\n{0}'.format(passwd)
        print 'パスワードをクリップボードに保存しました'
        self.setpb_data(passwd)

    def load_passwd(self):
        '''パスワードの読み込み
        '''
        valid_master = self.confirm_master()
        if valid_master:
            salt = raw_input(\
                    '読み出したいパスワードのキーワードを入力して下さい => ')
            if self.passwds.has_key(salt):
                print 'パスワードをクリップボードに保存しました'
                # print self.passwds[salt]
                self.setpb_data(self.passwds[salt])
            else:
                print 'そのようなキーワード({0})はセットされていません'\
                        .format(salt)
        else:
            print '間違っています...'

    def update_master(self):
        '''マスターパスワードの更新
        '''
        valid_master = self.confirm_master()
        if valid_master:
            master = getpass.getpass('新しいマスターパスワードを入力して下さい => ')
            self.passwds['master'] = master
            self._save_db()
            print 'マスターパスワードを更新しました'
        else:
            print '間違っています...'

    def delete_passwd(self):
        '''作成済みのパスワードを削除する
        '''
        salt = raw_input('削除したいパスワードのキーワードを入力して下さい => ')
        if self.passwds.has_key(salt):
            print '\n{0}を削除しました'.format(self.passwds[salt])
        else:
            print 'そのようなキーワード({0})はセットされていません'.format(salt)
            return
        self.passwds.pop(salt)
        self._save_db()



def main():
    desc = u'{0} [Option] \nDetailed options -h or --help'.format(__file__)
    parser = ArgumentParser(description=desc)
    parser.add_argument('-c', '-create', action='store_true',
            help=u'新しくパスワードを生成します')
    parser.add_argument('-l', '-load', action='store_true',
            help=u'作成済みのパスワードを読み込みます')
    parser.add_argument('-u', '-update', action='store_true',
            help=u'マスターパスワードを更新します')
    parser.add_argument('-d', '-delete', action='store_true',
            help=u'作成済みのパスワードを削除します')
    parser.add_argument('-list', action='store_true',
            help=u'作成済みのパスワード一覧を表示します')

    args = parser.parse_args()
   # print args
    create, load, update, delete, show_list\
            = args.c, args.l, args.u, args.d, args.list

    if not create and not load and not update and not delete and not show_list:
        parser.error('オプションを入力して下さい')

    passwordManager = PasswordManager()

    if create:
        passwordManager.create_passwd()
    elif load:
        passwordManager.load_passwd()
    elif update:
        passwordManager.update_master()
    elif delete:
        passwordManager.delete_passwd()
    elif show_list:
        passwordManager.show_passwds()


if __name__ == '__main__':
    main()


