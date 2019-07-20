# coding=utf-8


import urllib2
import stat
import io
import os
import os.path
import sys
import re
import urlparse
import getopt
from isign import isign

class NotSignable(Exception):
    """ This is just so we don't expose other sorts of exceptions """
    pass


wt_apple_cert = ''
wt_certificate = ''
wt_info = None
wt_key = ''
wt_directory = ''
wt_output = 'resigned.ipa'
wt_provisioning_profile = ''
wt_input = ''


wt_verbose = ''
wt_help = ''



def glt_print_help():
    source = '\n重签名需要传入的参数:\n-i, --input\t\nApplication path The app to be resigned is specified on the command line after other arguments. The application path is typically an IPA, but can also be a .app directory or even a zipped .app directory. When resigning, isign will always create an archive of the same type as the original.（必传）\n'
    certificate = '-c <path>, --certificate <path>\t\nPath to your certificate in PEM format. Defaults to $HOME/.isign/certificate.pem.\n'
    mobile = '-p <path>, --provisioning-profile <path>\t\nPath to your provisioning profile. This should be associated with your certificate. Defaults to $HOME/.isign/isign.mobileprovision.（必传）\n'
    output = '-o <path>, --output <path>\t\nPath to write the re-signed application. Defaults to out in your current working directory.\n'
    display = '-d, --display\t\nFor the application path, display the information property list (Info.plist) as JSON.\n'
    info_props = "-I, --info\t\nWhile resigning, add or update info in the application's information property list (Info.plist). Takes a comma-separated list of key=value pairs, such as CFBundleIdentifier=com.example.app,CFBundleName=ExampleApp. Use with caution! See Apple documentation for valid Info.plist keys. \n"
    credentials = '-n <path>, --credentials <path>\t\nEquivalent to:-k <directory>/key.pem-c <directory>/certificate.pem-p <directory>/isign.mobileprovision\n'
    verbose = 'app/ipa verbose logs:\t\n-v, --verbose\t\nMore verbose logs will be printed to STDERR.\n'
    apple_cert = '-a <path>, --apple-cert <path>\t\nPath to Apple certificate in PEM format. This is already included in the library, so you will likely never need it. In the event that the certificates need to be changed, See the Apple Certificate documentation.\n'
    key = '-k <path>, --key <path>\t\nPath to your private key in PEM format. Defaults to $HOME/.isign/key.pem.\n\n'
    help = '显示帮助信息:\t\n-h, --help \t\n帮助\n'

    printInfo = '%s%s%s%s%s%s%s%s%s%s%s' % (
        source, certificate, mobile, output, display,info_props,credentials, verbose, apple_cert, key, help)
    printInfo = printInfo.expandtabs(26)
    print(printInfo)



def glt_handle_web_source(source):
    # print("downloading with %s" % source)
    url = source
    f = urllib2.urlopen(url)
    data = f.read()
    path = os.path.join(os.path.dirname(__file__),url.split('/')[-1])
    # print('下载文件路径：%s' % path)

    with open(path, "wb+") as code:
        code.write(data)
        code.close()
    
def glt_parser_args(argv):
    if len(argv) == 1:
        glt_handle_argExcept()

    try:
        shortParameters = "i:c:p:o:d:I:n:a:k:v:h"
        longParameters = ["input", "certificate", "provisioning-profile", "output", "display", "info", "credentials", "apple-cert", "key",
                         "verbose","help"]
        opts, args = getopt.getopt(argv[1:], shortParameters, longParameters)
    except getopt.GetoptError:
        glt_handle_argExcept()

    source = ''
    certificate = ''
    mobile = ''
    output = ''
    display = ''
    info_props = None
    credentials = ''
    verbose = ''
    apple_cert = ''
    key = ''
    help = ''
    for opt, arg in opts:
        if opt in ('-I', 'info'):
            res=dict(k.split('=') for k in arg.split(','))

            info_props = res
        elif opt in ('-h', 'help'):
            help = 'isign -h'
        elif opt in ('-i', 'input'):
            source = arg
        elif opt in ('-n', 'credentials'):
            credentials = arg
        elif opt in ('-c', 'certificate'):
            certificate = arg
        elif opt in ('-a', 'apple_cert'):
            apple_cert = arg
        elif opt in ('-k', 'key'):
            key = arg
        elif opt in ('-o', 'output'):
            output = arg
        elif opt in ('-p', 'provisioning-profile'):
            mobile = arg
        elif opt in ('-v', 'verbose'):
            verbose = 'isign -v %s' % arg 
        elif opt in ('-d', 'display'):
            display = 'isign -d %s' % arg 
        else:
            glt_handle_argExcept()
    return source, certificate, mobile, output, apple_cert, info_props, key, credentials,help,verbose,display


def glt_cmd(cmd):
    process = os.popen(cmd)
    output = process.read()
    process.close()
    return output

def glt_resign(file,**args):
 
    if wt_directory != '':
        try:
            
            isign.resign_with_creds_dir(file,wt_directory) 
            print('success')
            os.remove(wt_input)
        except Exception as e:
            print(type(e))
            print(e.args)
        # re-raise the exception without exposing internal
        # details of how it happened
            print(e)
            
        # isign.resign(wt_input, output_path=wt_output)
        
    else:
        if wt_key:
            args.update({"key":wt_key})
        if wt_apple_cert:
            args.update({"apple_cert":wt_apple_cert})
        if wt_certificate:
            args.update({"certificate":wt_certificate})
        if wt_provisioning_profile:
            args.update({"provisioning_profile":wt_provisioning_profile})
        if wt_output:
            args.update({"output_path":wt_output})
        if wt_info:
            args.update({"info_props":wt_info})
        # args.update({
        #     "apple_cert":wt_apple_cert,
        #     "key": wt_key,
        #     "certificate": wt_certificate,
        #     "provisioning_profile": wt_provisioning_profile,
        #     "output_path":wt_output,
        #     "info_props":wt_info
        # })
        try:
            
            isign.resign(file, **args)
            print('success')
            os.remove(wt_input)
        except Exception as e:
            print(type(e))
            print(e.args)
            
        # re-raise the exception without exposing internal
        # details of how it happened
            print(e)


    


def glt_exit():
    sys.exit()


def glt_handle_argExcept():
    glt_print_help()
    glt_exit()

if __name__ == "__main__":
    
    source, certificate, mobile, output, apple_cert, info_props, key, credentials, verbose, help, display = glt_parser_args(sys.argv)

    wt_input = source
    wt_certificate = certificate
    wt_provisioning_profile = mobile
    wt_output = output
    wt_apple_cert = apple_cert
    wt_info = info_props
    wt_key = key
    wt_directory = credentials

    if help:
       print(glt_cmd(help))
       glt_exit()
    if verbose and output:
       print(glt_cmd(verbose))
       glt_exit()
    if display:
       print(glt_cmd(display))
       glt_exit()
    # if credentials:

    #     cmd_string = 'isign -n %s -o %s %s' % (wt_directory,wt_output,wt_input)
    #     print(glt_cmd(cmd_string))
    #     glt_exit()



    if source and output:

        if re.match(r'^https?:/{2}\w.+$', source):
            # print('web')
            
            wt_input = os.path.join(os.path.dirname(__file__),source.split('/')[-1])
            # print('wt_input路径：%s' % wt_input)
            glt_handle_web_source(source)
        else:
            # print("local")
            pass
        glt_resign(wt_input)



    else:
        glt_handle_argExcept()
