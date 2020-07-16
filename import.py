import sys
import os
import uuid
import os.path

SRC_CODE_PATH = 1
OUTPUT_DIR = 2
PROJ_NAME = 3
FILTER = 4

VCXPROJ_FILE = "vcxproj.files.txt"
VCXPROJ_FILTER = "vcxproj.filters.txt"
VCXPROJ_FILTER_AND_FILE = "vcxproj.filters.files.txt"

INVALID_XML_CHAR  = ['<','>','&', '\"', '\'',';']
def remove_invalid_xml_char(str):
    for e in INVALID_XML_CHAR:
        str = str.replace(e, '?')
    return str

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def out_rel_path_to_src_dir(src_dir,output_dir):
    dir_in_cwd = output_dir.upper().split("\\")
    dir_in_abs_path = src_dir.upper().split("\\")    
    while len(dir_in_cwd) > 0 and len(dir_in_abs_path) > 0 and dir_in_cwd[0] == dir_in_abs_path[0]:
        dir_in_abs_path.pop(0)
        dir_in_cwd.pop(0)

    rel_path = ""
    while len(dir_in_cwd) > 0:
        rel_path = rel_path + "..\\"
        dir_in_cwd.pop(0)
    
    for dir in dir_in_abs_path:
        rel_path = rel_path + dir

    return rel_path

def create_vcxproj(output_dir,proj_name):
    vcxproj_dir = output_dir + "\\" + proj_name + "\\" + proj_name
    if not os.path.exists(vcxproj_dir):
        os.makedirs(vcxproj_dir)

    gen_vcxproj = open(vcxproj_dir  +  "\\" + proj_name + ".vcxproj","w")
    vcxproj_cfg = open("config\\template_parser.vcxproj","r")
    for line in vcxproj_cfg:
        gen_vcxproj.write(line)
        if "${INSERT_C1}" in line:
            vcxproj = open(VCXPROJ_FILE,"r")
            for file in vcxproj:
                gen_vcxproj.write(file)    

def create_vcxproj_filter(output_dir,proj_name):
    vcxproj_dir = output_dir + "\\" + proj_name +  "\\" + proj_name 
    if not os.path.exists(vcxproj_dir):
        os.makedirs(vcxproj_dir)

    gen_vcxproj_filter = open(vcxproj_dir  +  "\\" + proj_name + ".vcxproj.filters","w")
    vcxproj_cfg_filter = open("config\\template_parser.vcxproj.filters","r")
    for line in vcxproj_cfg_filter:
        gen_vcxproj_filter.write(line)
        if "${INSERT_FILTER}" in line:
            vcxproj = open(VCXPROJ_FILTER,"r")
            for file in vcxproj:
                gen_vcxproj_filter.write(file)  
        
        if "${INSERT_FILTER}" in line:
            vcxproj = open(VCXPROJ_FILTER_AND_FILE,"r")
            for file in vcxproj:
                gen_vcxproj_filter.write(file)  

def create_solution(output_dir,proj_name):

    sol_dir = output_dir + "\\" + proj_name
    if not os.path.exists(sol_dir):
        os.makedirs(sol_dir)

    sln = open(sol_dir + "\\" + proj_name + ".sln","w")

    sln_template = open("config\\parser.sln")
    for line in sln_template:
        if "${PROJ_NAME}" in line:
            line=line.replace("${PROJ_NAME}",proj_name)
        sln.write(line)
    sln.close()   

def generate_project_files(src_dir,output_dir,proj_name,filter):

    allowable_extension = [ "." + x for x in filter.split(";") ]
    allowed_all = False
    if filter == "*.*"  or filter == ".*":
        allowed_all = True

    vcxproj_files = open(VCXPROJ_FILE,"w")
    vcxproj_filter_with_files = open(VCXPROJ_FILTER_AND_FILE,"w")
    vcxproj_filter = open(VCXPROJ_FILTER,"w")    

    src_stack = []
    src_stack.append(src_dir)

    filter_stack = ["Source"]
    rel_path_src_stack = []
    rel_path_src_stack.append(out_rel_path_to_src_dir(src_dir,output_dir + "\\" + proj_name +  "\\" + proj_name))

    counter = 0
    while(len(src_stack) > 0):
        src_path_dir = src_stack.pop()
        filter_path_dir = filter_stack.pop()
        rel_path_dir = rel_path_src_stack.pop()

        try:


            vcxproj_filter.write("<Filter Include=\"{}\">\n".format(remove_invalid_xml_char(filter_path_dir)));
            vcxproj_filter.write("<UniqueIdentifier>{}</UniqueIdentifier>\n".format(uuid.uuid1()));
            vcxproj_filter.write("</Filter>\n")

            for f in os.listdir(src_path_dir):
                src_path = os.path.join(src_path_dir,f)
                rel_path = rel_path_dir + "\\" + f

                if os.path.isdir(src_path) == True:
                    src_stack.append(src_path)
                    filter_path = os.path.join(filter_path_dir,f)
                    filter_stack.append(filter_path)
                    
                    rel_path_src_stack.append(rel_path)
                else:
                    file_extension = os.path.splitext(src_path)[1]
                     
                    if  allowed_all == True or file_extension in allowable_extension :   
                        rel_path = remove_invalid_xml_char(rel_path)
                        vcxproj_files.write("<ClCompile Include=\"{}\"/>\n".format(rel_path))

                        vcxproj_filter_with_files.write("<ClCompile Include=\"{}\">\n".format(rel_path))
                        vcxproj_filter_with_files.write("<Filter>{}</Filter>\n".format(remove_invalid_xml_char(filter_path_dir)))
                        vcxproj_filter_with_files.write("</ClCompile>\n")

                    counter = counter + 1
                    if counter % 1000 == 0:
                        print("\rProcessing file # {}".format(counter), end="\r")

        except KeyboardInterrupt:
            print("Exiting ...")
            sys.exit(1)                 
        except:
            print("Error encountered in " + src_path)
    vcxproj_files.close()
    vcxproj_filter_with_files.close()
    vcxproj_filter.close()

def check_config():
    if (os.path.exists("config\\parser.sln") == False) or (os.path.exists("config\\template_parser.vcxproj.filters") == False)  or (os.path.exists("config\\template_parser.vcxproj") == False) :
        print("Missing config. files...")
        return False
    return True


def check_arg(arg):

    if len(arg) < 4  :
        print("Usage: <file>.py <source code absolute path> <output directory absolute path> <project name> filter( <file type>;<file type>... ) - Invalid source code path")
        return         
    else:
        if os.path.isdir(sys.argv[SRC_CODE_PATH]) == False:
            print("Usage: <file>.py <source code absolute path> <output directory absolute path> <project name> filter( <file type>;<file type>... ) - Invalid source code path")
            return False
        elif os.path.isdir(sys.argv[OUTPUT_DIR]) == False:
            print("Usage: <file>.py <source code absolute path> <output directory absolute path> <project name> filter( <file type>;<file type>... ) - Invalid output directory")  
            return False  
        else:
            return True
 
if __name__ == "__main__":
    if check_config() == True:
        if check_arg(sys.argv) == True:
            filter=""
            if len(sys.argv) > 4:
                filter = sys.argv[FILTER]

            generate_project_files(sys.argv[SRC_CODE_PATH],sys.argv[OUTPUT_DIR],sys.argv[PROJ_NAME],filter)   
            create_solution(sys.argv[OUTPUT_DIR],sys.argv[PROJ_NAME])
            create_vcxproj(sys.argv[OUTPUT_DIR],sys.argv[PROJ_NAME])
            create_vcxproj_filter(sys.argv[OUTPUT_DIR],sys.argv[PROJ_NAME])




