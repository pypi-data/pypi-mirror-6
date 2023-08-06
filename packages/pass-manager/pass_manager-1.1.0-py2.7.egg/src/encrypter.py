# -*- encoding:utf-8 -*-
'''
file Encrypter for pass-manager
'''
import crypto
import os


class Encrypter(object):
    ''' file encrypter
    '''
    # key files
    PRIVATE = '{home}/.ssh/.pass-manager_rsa'.format(home=os.environ['HOME'])
    PUBLIC = '{home}/.ssh/.pass-manager_rsa.pub'.format(home=os.environ['HOME'])

    def __init__(self):
        self.public = None
        self.private = None
        if not os.path.exists(self.PRIVATE) or not os.path.exists(self.PUBLIC):
            # first time to use Encrypter, create key files
            self.public, self.private = crypto.newkeys(512)
            self.save_secret_files()


    def save_secret_files(self):
        ''' save public, private keys
        '''
        crypto.export_key_file(self.public, self.PUBLIC)
        crypto.export_key_file(self.private, self.PRIVATE)
        return True

    def load_secret_files(self):
        ''' set public, private keys to self
        '''
        if not self.public and not self.private:
            self.public = crypto.load_key_file(self.PUBLIC)
            self.private = crypto.load_key_file(self.PRIVATE)

    def decrypt(self, encrypted_file_content):
        ''' decrypt encrypted_file_content
        '''
        self.load_secret_files()
        decrypted_file_content = crypto.decrypt(encrypted_file_content, self.private)
        return decrypted_file_content

    def encrypt(self, file_content):
        ''' encrypt not_encrypted_file_content
        '''
        self.load_secret_files()
        encrypted_file_content = crypto.encrypt(file_content, self.public)
        return encrypted_file_content
