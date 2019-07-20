# coding=utf-8
import urllib2
import getopt
import os
import shutil
import sys
import time
import zipfile
import urlparse
import re
import platform
import stat
import io

linux_isign = os.path.join(os.path.dirname(__file__),'wt_isign_linux.py')
# print(linux_isign)
macos_isign = os.path.join(os.path.dirname(__file__),'wt_isign_macos.py')

# print(macos_isign)

wt_apple_cert = ''
wt_p12 = os.path.join(os.path.dirname(__file__),'certificate.p12')
wt_certificate = os.path.join(os.path.dirname(__file__),'certificate.pem')
wt_info = None
wt_key = os.path.join(os.path.dirname(__file__),'key.pem')
wt_directory = ''
wt_output = os.path.join(os.path.dirname(__file__),'resigned.ipa')
wt_provisioning_profile = ''
wt_input = ''

wt_version = '1.0.0'
wt_verbose = ''
wt_help = ''
wt_bundle_identifier = ''
wt_display_name = ''


def glt_print_help():
    source = '\n重签名需要传入的参数:\n-i, --input\t源App/ipa的路径（必传）\n'
    certificate = '-c, --certificate\t证书pem\n'
    key = '-k, --key\t公钥pem\n'


    mobile = '-p, --provisioning-profile\tembedded.mobileprovision路径（必传）\n'
    output = '-o, --output\tipa导出路径（可选，默认当前路径）\n'
    info = '-I, --info\t更新Info.plist里面的信息，比如BundleIdentifier,Version,DisplayName等（可选，默认为原始）Takes a comma-separated list of key=value pairs, such as CFBundleIdentifier=com.example.app,CFBundleName=ExampleApp\n\n'

    encrypt = 'app/ipa是否加密:\n-e, --encrypt\t根据app/ipa路径判断可执行文件是否加密,linux下这个命令无效\n\n'

    codesignID = '获取证书签名id:\n-l, --codesignid\t证书签名id,linux下这个命令无效\n\n'

    version = '当前工具的版本:\n-v, --version \t版本号\n\n'

    help = '显示帮助信息:\n-h, --help \t帮助\n'
    display = '显示app详细信息：\n-d,--display \tlinux下展示app信息\n'

    printInfo = '%s%s%s%s%s%s%s%s%s%s%s' % (
        source, certificate,key, mobile, output, info, codesignID, encrypt, version, help,display)
    printInfo = printInfo.expandtabs(26)
    # print(printInfo)


def glt_exit():
    sys.exit()


def glt_handle_argExcept():
    glt_print_help()
    glt_exit()


def glt_cmd(cmd):
    process = os.popen(cmd,'r')
    output = process.read()
    output
    process.close()
    return output

def glt_parser_args(argv):
    if len(argv) == 1:
        glt_handle_argExcept()

    try:
        shortParamters = "vhi:c:k:I:d:p:o:e:l"
        longParamters = ["version", "help", "input","certificate", "key","info", "display", "provisioning-profile", "output", "encrypt","codesignid"]
        opts, args = getopt.getopt(argv[1:], shortParamters, longParamters)
    except getopt.GetoptError:
        glt_handle_argExcept()

    source = ''
    mobile = ''
    output = ''
    version = ''
    codesignID = ''
    encrypt = ''
    certificate = ''
    key = ''
    info = None
    display = ''


    for opt, arg in opts:
        if opt == '-v' or opt == '--version':
            version = wt_version
        elif opt in ('-h', 'help'):
            glt_handle_argExcept()
        elif opt in ('-i', 'input'):
            source = arg
        
        elif opt in ('-I', 'info'):
            info = arg
        elif opt in ('-k', 'key'):
            key = arg
            wt_key = key
        elif opt in ('-d','display'):
            display = arg
        elif opt in ('-c', 'certificate'):
            certificate = arg
            wt_certificate = certificate
        elif opt in ('-p', 'provisioning-profile'):
            mobile = arg
        elif opt in ('-o', 'output'):
            output = arg
        elif opt in ('-e', 'encrypt'):
            encrypt = arg
        elif opt in ('-l', 'codesignid'):
            codesignID = 'security find-identity -v -p codesigning'
        else:
            glt_handle_argExcept()
    return source, info, certificate,key, mobile, output, codesignID, encrypt, version,display



if __name__ == '__main__':
    
    
    sysstr = platform.system().lower()


    
    if 'darwin' in sysstr:
        source, info, certificate,key, mobile, output, codesignID, encrypt, version,display = glt_parser_args(sys.argv)
        
            
        if codesignID:
            glt_cmd(codesignID)
            glt_exit()
        if version:
            cmd = 'python %s -V' % (macos_isign)
            glt_cmd(cmd)
            glt_exit()
        if encrypt:
            cmd = 'python %s -e %s' % (macos_isign,encrypt)
            glt_cmd(cmd)
            glt_exit()
        if wt_certificate  and wt_key :
            cmd = 'openssl pkcs12 -export -in %s -out %s -inkey %s -passin "pass:123456" -passout "pass:123456"' % (wt_certificate,wt_p12,wt_key)
            glt_cmd(cmd)
            
            unlock_keychain = "security unlock-keychain -p '123456' /srv/www/Library/Keychains/www.keychain"
            glt_cmd(unlock_keychain)
            list_keychain = "security list-keychains -s /srv/www/Library/Keychains/www.keychain"
            glt_cmd(list_keychain)
            cert_import = "security import %s -k /srv/www/Library/Keychains/www.keychain -P 123456 -T /usr/bin/codesign -A /usr/bin/codesign" % wt_p12
            glt_cmd("chmod 777 %s" % wt_p12)
            # print(cert_import)
            glt_cmd(cert_import)
            wt_dict = {}
            cmd = "cat %s 2>/dev/null | grep 'friendlyName'" % wt_certificate
            certificateID = glt_cmd(cmd)
            # print(certificateID)
            certificateID = certificateID.strip().replace('friendlyName:','').strip()
            # print(certificateID)


            if certificateID:
                wt_dict.update({'-d':'\"%s\"' % certificateID})
            if source:
                wt_dict.update({'-i': source})
            if mobile:
                wt_dict.update({'-m': mobile})
            if output:
                wt_dict.update({'-o': output})
            if info:
                res=dict(k.split('=') for k in info.split(','))
                wt_dict.update({'-n':'\"%s\"' % res["CFBundleDisplayName"]})
                wt_dict.update({'-b':'\"%s\"' % res["CFBundleIdentifier"]})

                    # res=dict(k.split('=') for k in arg.split(','))
                    # openssl pkcs12 -nodes -in p12证书路径 -info -nokeys -passin 'pass:bingniao' 2>/dev/null | grep 'friendlyName'

            base = 'python %s' % macos_isign
        
            for (key,value) in wt_dict.items():  
                base = base + ' %s %s' % (key,value)
            # print(base)
            result = glt_cmd(base)
            if 'success' in result:
                print('success')
            else:
                print('failure')
            glt_exit()
        
 
    elif 'windows' in sysstr:
        source, info, certificate,key, mobile, output, codesignID, encrypt, version,display = glt_parser_args(sys.argv)
        if display:
            glt_cmd('python %s -d %s' % (linux_isign,display))
            glt_exit()

        wt_dict = {}
        if source:
            wt_dict.update({'-i':source})
        if info:
            wt_dict.update({'-I':info})
        if certificate:
            wt_dict.update({'-c':certificate})
        if key:
            wt_dict.update({'-k':key})
        if mobile:
            wt_dict.update({'-p':mobile})
        if output:
            wt_dict.update({'-o':output})
        base = 'python %s' % linux_isign

        for (key,value) in wt_dict.items():  
             base = base + ' %s %s' % (key,value)
        result = glt_cmd(base)
        if 'success' in result:
            print('success')
        else:
            print('failure')
        glt_exit()
    elif 'linux' in sysstr:
        source, info, certificate,key, mobile, output, codesignID, encrypt, version,display = glt_parser_args(sys.argv)
        if display:
            glt_cmd('python %s -d %s' % (linux_isign,display))
            glt_exit()

        wt_dict = {}
        if source:
            wt_dict.update({'-i':source})
        if info:
            wt_dict.update({'-I':info})
        if certificate:
            wt_dict.update({'-c':certificate})
        if key:
            wt_dict.update({'-k':key})
        if mobile:
            wt_dict.update({'-p':mobile})
        if output:
            wt_dict.update({'-o':output})
        base = 'python %s' % linux_isign

        for (key,value) in wt_dict.items():  
             base = base + ' %s %s' % (key,value)
        # print(base)
        result = glt_cmd(base)
        if 'success' in result:
            print('success')
        else:
            print('failure')
        

        glt_exit()


    