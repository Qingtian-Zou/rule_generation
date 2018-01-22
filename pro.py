import argparse
import os
from anytree import Node, RenderTree

FLAGS=None

def main():
    root=Node(os.path.split(FLAGS.log)[1])
    batch=[]
    rawdata=open(FLAGS.log,'r')
    rawdata=rawdata.readlines()
    for line in rawdata:
        batch.append(line)
    
    # Up until now, all the raw data inside log file are inside batch[]
    for i in range(len(batch)):
        found=False
        # Loop for all the lines
        pid=batch[i][0:5].replace(' ','')
        # Search for node with the name of pid
        # if it does not exist, create a new leaf
        for nd in root.children:
            if nd.name==pid:
                tmp=Node(batch[i].split(' ',1)[1],parent=nd)
                found=True
                break
        if not found:
            tpnd=Node(pid,parent=root)
            tend=Node(batch[i].split(' ',1)[1],parent=tpnd)
    
    # Up until now, all the raw data are sorted into a tree whose structure is formed as below:
    # root (log file name)
    # ├─(pid)
    # │  ├─(entries,start with a detailed time stamp which takes 15 slots, follwed by the system call after a whitespace)
    # ··················································

    # Recognition and processing
    target0=[] # Record the uninstalled software
    target1=['execve','apt','remove'] # Flage1: starting uninstall
    target2=['exited with 0'] # Flage2: Unistall process exit without error --> uninstall succeed
    # unistallFlag:
    # 0 --> not start uninstalling
    # 1 --> started but not finished
    # 2 --> finished successfully
    for pidNode in root.children:
        uninstallFlag=0
        for entryNode in pidNode.children:
            hit=0
            for t in target1:
                if t in entryNode.name:
                    hit+=1
            if hit == 3:
                uninstallFlag=1
                target0.append(entryNode.name.split('\"')[7])
                hit=0
                continue
            for t in target2:
                if (t in entryNode.name) and (uninstallFlag == 1):
                    uninstallFlag=2
        if uninstallFlag ==1:
            del target0[len(target0)-1]
    if target0!=[]:
        for sw in target0:
            print(sw+' is unistalled. All entries concerning it should be removed.')

    # Load rule file, make chages
    fi0=open(FLAGS.rule,'r') # Load original rule file
    fi1=open('new_'+os.path.split(FLAGS.rule)[1],'w') # Create new rule file
    rules=fi0.readlines()
    changed=False
    for line in rules:
        # If the unistalled software appears in the rule, skip this line; else, copy this line to the new file
        for usw in target0:
            if usw in line:
                changed=True
                continue
        fi1.write(line)
    fi0.close()
    fi1.close()
    if not changed: # If no chages are made, remove the new rule file.
        os.remove(os.path.join(os.getcwd(),'new_'+os.path.split(FLAGS.rule)[1]))
        print('No need to change rule file.')
    else:
        print('Revised rule file ceated at '+os.path.join(os.getcwd(),'new_'+os.path.split(FLAGS.rule)[1]))

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    # TODO: change these into files instead of folders
    parser.add_argument(
        '--log',
        type=str,
        default='',
        help='Path to the log file.'
    )
    parser.add_argument(
        '--rule',
        type=str,
        default='',
        help='Path to the rule file'
    )
    FLAGS, unparsed = parser.parse_known_args()
    main()