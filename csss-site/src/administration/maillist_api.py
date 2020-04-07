import pysftp

class SFUMailllist:

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        try:
            with pysftp.Connection(self.hostname, username=self.username, password=self.password) as sftp:
                print(sftp.execute(f"touch /home/{username}/file"))
        except FileNotFoundError as e:
            print(f" the private_key was not found \n {e}")

    def add_users_to_maillist(self, users, maillist):
        file = open("maillist.txt","w")
        for user in users:
            file.write(f"{user}\n")
        file.close()
        with pysftp.Connection(self.hostname, username=self.username, password=self.password) as sftp:
            with sftp.cd(f"/home/{username}/"):
                sftp.put("testfile.txt")
                print(sftp.execute(f"maillist modify {maillist} members maillist.txt "))
