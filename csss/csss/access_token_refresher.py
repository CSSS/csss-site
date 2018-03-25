import time
import oauth2

class DateTime:

	day=0
	month=0
	year=0
	hour=0
	minute=0
	second=0

	def __init__():
		current_time=time.strftime("%Y-%m-%d-%H-%M-%S")
		year=current_time[:4]
		month=current_time[5:7]
		day=current_time[8:10]
		hour=current_time[11:13]
		minute=current_time[14:16]
		second=current_time[-2:]

	def compare(date):

		if (self.hour != date[11:13]):
			return RefreshToken("449132530651-etnu8h6phobha55v5u5a7ur22sphc1av.apps.googleusercontent.com", "AQ1HizrYfPeb4KSPW5Adbr_A","1/ZkDDymOswmfEdsUm4Bl5Of5E8DsXDbadStuENqkp_hc3yE8XiOQyJ-00ZhqWETRM")

		if (self.day != date[8:10]):
			return RefreshToken("449132530651-etnu8h6phobha55v5u5a7ur22sphc1av.apps.googleusercontent.com", "AQ1HizrYfPeb4KSPW5Adbr_A","1/ZkDDymOswmfEdsUm4Bl5Of5E8DsXDbadStuENqkp_hc3yE8XiOQyJ-00ZhqWETRM")

		if (self.month != date[5:7]):
			return RefreshToken("449132530651-etnu8h6phobha55v5u5a7ur22sphc1av.apps.googleusercontent.com", "AQ1HizrYfPeb4KSPW5Adbr_A","1/ZkDDymOswmfEdsUm4Bl5Of5E8DsXDbadStuENqkp_hc3yE8XiOQyJ-00ZhqWETRM")

		if (self.year != self[:4]):
			return RefreshToken("449132530651-etnu8h6phobha55v5u5a7ur22sphc1av.apps.googleusercontent.com", "AQ1HizrYfPeb4KSPW5Adbr_A","1/ZkDDymOswmfEdsUm4Bl5Of5E8DsXDbadStuENqkp_hc3yE8XiOQyJ-00ZhqWETRM")
		return False

def main():
	last_update_reader = open('LATEST_UPDATE', 'r')
	current_time = DateTime()
	refresh_token=current_time.compare(last_update_reader.readline())
	last_update_reader.close()

	if (refresh_token != False):
		update_last_update_file = open('LATEST_UPDATE', 'w')
		update_last_update_file.write(time.strftime("%Y-%m-%d-%H-%M-%S")) 
		update_last_update_file.close()
		gmail_file = open('/usr/local/lib/python3.5/dist-packages/django_mailbox/transports/gmail.py', 'w')
		with open('/usr/local/lib/python3.5/dist-packages/django_mailbox/transports/gmail-1') as top_half:
			gmail_file.write(top_half.readline()+"\n")
		gmail_file.write("                access_token = "+refresh_token+"\n")
		with open('/usr/local/lib/python3.5/dist-packages/django_mailbox/transports/gmail-2') as bottom_half:
			gmail_file.write(bottom_half.readline()+"\n")
		gmail_file.close()
	else:
		#was not updated

if __name__ == '__main__':
	main()