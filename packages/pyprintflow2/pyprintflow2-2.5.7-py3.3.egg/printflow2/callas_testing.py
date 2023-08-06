'''
Created on 17 Mar 2014

@author: "Colin Manning"
'''

import os
import subprocess
import hashlib
import time
import traceback
import sys
import getopt

import utils


activation_code = "XAJT69YLX6TPEW9LT69JTKDY"
pdftoolbox_path = '/opt/callas/callas_pdfToolbox_CLI_7_x64/pdfToolbox.bin'
cache_path = '/opt/printflow2/callas/cache'
report_folder = '/opt/printflow2/tmp'
help_text = 'usage:\n printflow2 -s <serial> -p <profile> -d <dest>  -f <file>'
serial_number = ""
profile = ''
file_path = ''
file_name = ''
file_pathname = ''
dest_folder = ''

def do_it():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"sfpdh:s:f:p:d:h",["serial=", "file=", "profile=","dest=","help", ])
    except getopt.GetoptError:
        print('Problem getting options')
        traceback.print_exc()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_text)
            sys.exit()
        elif opt in ("-s", "--serial"):
            serial_number = arg
        elif opt in ("-p", "--profile"):
            profile = arg
        elif opt in ("-d", "--dest"):
            dest_folder = arg
        elif opt in ("-f", "--file"):
            file_pathname = arg
            sp = os.path.split(file_pathname)
            file_path = sp[0]
            file_name = sp[1]
            
    print("Serial Number: ", serial_number)
    print("Profile: ", profile)
    print("Destination: ", dest_folder)
    print("File: ", file_pathname)
    
    ok, info = preflight_check(file_path, file_name, file_pathname, profile, serial_number, dest_folder)
    print('OK: ', ok)
    print('Info: "', info, '"')

def preflight_check(file_path, file_name, file_pathname, profile, serial_number, dest_folder):
    ok = False
    info = ''
    try:
        print("Preflight checking file:" + file_pathname)
        status = run_job(serial_number, file_path, file_name, profile, dest_folder)
        if status == 0:
            ok = True;
            info = 'Good - No problems'
        elif status == 1:
            ok = True
            info = 'Good - Some possible issues'
        elif status == 2:
            ok = False
            info = 'Good - Some warnings'
        elif status == 3:
            ok = False
            info = 'Fail - Not compliant'
        elif status == 5:
            ok = True
            info = 'Good - No problems, file corrected'
        elif status == 103:
            ok = True
            info = 'Fail - Error processing file'
        elif status == 104:
            ok = True
            info = 'Fail - Cannot open file'
        else:
            ok = False
            
    except:
        print('Error in pre-flight process!')
        print(traceback.format_exc())
        traceback.print_exc()
            
        return ok, info
    
def run_job(serial_no, file_path, file_name, profile, dest_folder):
    status = -1
    try:
        theFile = os.path.join(file_path, file_name)  
                
        report_file_text = os.path.join(dest_folder, 'report_'+ utils.removeNonAscii(file_name)+'.txt')
        if os.path.exists(report_file_text):
            try:
                os.remove(report_file_text)
            except:
                print('Problem removing tmp text report file: '+report_file_text)
                
        report_file_html = os.path.join(dest_folder, 'report_'+ utils.removeNonAscii(file_name)+'.html')
        if os.path.exists(report_file_html):
            try:
                os.remove(report_file_html)
            except:
                print('Problem removing tmp html report file: '+report_file_html)
                   
        print('Processing file:' + theFile)
        #license = self.get_license(serial_no)
        #print "License:", license
        processResult = None
        
        
        callas_license = str(get_license(serial_no))
        print('License: ', callas_license)
        cmd = ['"'+str(pdftoolbox_path)+'"', '--license='+str(serial_no), '--secret='+callas_license, \
                '--nosummary', '--noprogress', '--nohits', '--nofixups', \
                '--report=XSLT=compacttext_point,ALWAYS,PATH="'+str(report_file_text)+'"', \
                '--report=XSLT=compacthtml_point,ALWAYS,PATH="'+str(report_file_html)+'"', \
                '"'+str(profile)+'"', '"'+str(theFile)+'"']
        print('Command Array: ', cmd)
        cmd_str = ' '.join(cmd)
        print('Command: ', cmd_str)
        p = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processResult = p.communicate()
        if p.returncode is not None:
            status = p.returncode
    except subprocess.CalledProcessError:
        # check return status to see what pdftoolbox thinks
        print('Problem calling command: '+str(cmd))
        traceback.print_exc()
    return status, processResult[0].decode()

def get_license(serial_no):
    this_check_time = time.strftime('%Y-%m-%d-%H-%M', time.localtime())        
    secret = '<' + activation_code + "><" + this_check_time + "><" + serial_no + ">";
    return hashlib.md5(secret.encode('utf-8')).hexdigest()

if __name__ == '__main__':
    do_it()
    