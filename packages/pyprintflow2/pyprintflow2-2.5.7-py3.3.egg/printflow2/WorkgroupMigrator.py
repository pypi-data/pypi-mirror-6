'''
Created on Jan 31, 2014

@author: "Colin Manning"
'''
from .JDs import JDs
import os
import getopt
import sys
from django.core.exceptions import ObjectDoesNotExist

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from workgroups.models import Workgroup, Client, User

def main():
    workgroupId = None
    help_text = 'usage:\n workgroup_migrator -w <workgroup>'
    try:
        opts, args = getopt.getopt(sys.argv[1:],"vhc:w",["workgroup="])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-w", "--workgroup"):
            workgroupId = arg
    jds = JDs('/opt/printflow2/db', 503, 502)
    jds.register_class('workgroup')
    try:
        json_workgroup = jds.fetch('workgroup', workgroupId)
        try:
            dj_workgroup = Workgroup.objects.get(noosh_id=workgroupId)
        except ObjectDoesNotExist:
            dj_workgroup = Workgroup()
            dj_workgroup.noosh_id = json_workgroup['id']
            dj_workgroup.name = json_workgroup['name']
            dj_workgroup.os_user_name =  json_workgroup['os_user_name']
            dj_workgroup.os_group_name =  json_workgroup['os_group_name']
            dj_workgroup.os_userid =  json_workgroup['os_userid']
            dj_workgroup.os_groupid =  json_workgroup['os_groupid']
            dj_workgroup.preflight_profile = json_workgroup['preflight_profile']
            dj_workgroup.dropbox_root = json_workgroup['dropbox_root']
            dj_workgroup.serial_number =  json_workgroup['serial_number']
            dj_workgroup.dam_site =  json_workgroup['dam_site']
            dj_workgroup.last_check = json_workgroup['last_check']
            if json_workgroup['id_parent'] > 0:
                try:
                    p = Workgroup.objects.get(noosh_id=json_workgroup['id_parent'])
                    dj_workgroup.parent =  p
                except ObjectDoesNotExist:
                    pass
            dj_workgroup.save()
            for json_client in json_workgroup['clients']:
                dj_client = Client()
                dj_client.name = json_client['name']
                dj_client.save()
                for json_user in json_client['users']:
                    # look for existing user - email is unique key
                    try:
                        dj_user = User.objects.get(email=json_client['email'])
                    except ObjectDoesNotExist:
                        dj_user.first_name = json_user['first_name']
                        dj_user.last_name = json_user['last_name']
                        dj_user.email = json_user['email']
                        dj_user.noosh_username = json_user['noosh_username']
                        dj_user.dropbox_name = json_user['dropbox_name']
                        dj_user = User()
                    dj_user.save()
                    dj_client.users.add(dj_user)
                    dj_client.save()
                dj_workgroup.clients.add(dj_client)
    except:
        print('problem getting workgroup with id: ', workgroupId)
        
if __name__ == '__main__':
    main()      
