#NAME: Mingchao Lian, Seoyoon Jin
#EMAIL: lianmccc@ucla.edu, seoyoonjin@g.ucla.edu
#ID: 005348062, 505297593

import sys, csv

bfree = [] # list of free blocks
ifree = [] # list of free inodes
inodes = [] # list of inodes
dir_entries = [] # list of dir entries
indirect_blocks = [] # list of indirect blocks


class superblock:
    def __init__(self,line):
        self.s_blocks_count = int(line[1])      # total number of blocks 
        self.s_inodes_count = int(line[2])      # total number of i-nodes
        self.block_size = int(line[3])          # block size (in bytes, decimal)
        self.s_inode_size = int(line[4])        # i-node size (in bytes, decimal)
        self.s_blocks_per_group = int(line[5])  # blocks per group (decimal)
        self.s_inodes_per_group = int(line[6])  # i-nodes per group (decimal)
        self.s_first_ino = int(line[7])         # first non-reserved i-node (decimal)

class group:
    def __init__(self,line):
        self.s_block_group_nr = int(line[1])            # group number (decimal, starting from zero)
        self.num_blocks_in_this_group = int(line[2])    # total number of blocks in this group (decimal)
        self.num_inodes_in_this_group = int(line[3])    # total number of i-nodes in this group (decimal)
        self.bg_free_blocks_count = int(line[4])        # number of free blocks (decimal)
        self.bg_free_inodes_count = int(line[5])        # number of free i-nodes (decimal)
        self.bg_block_bitmap = int(line[6])             # block number of free block bitmap for this group (decimal)
        self.bg_inode_bitmap = int(line[7])             # block number of free i-node bitmap for this group (decimal)
        self.bg_inode_table = int(line[8])              # block number of first block of i-nodes in this group (decimal)

class inode:
    def __init__(self,line):
        self.inode_num = int(line[1])           # inode number (decimal)
        self.file_type = line[2]                # file type (char)
        self.mode = int(line[3])                # inode.i_mode & 0xFFF, mode (low order 12-bits, octal)
        self.i_uid = int(line[4])               # owner (decimal)
        self.i_gid  = int(line[5])              # group (decimal)
        self.i_links_count = int(line[6])       # link count (decimal)
        self.ctime_str = line[7]                # time of last I-node change (mm/dd/yy hh:mm:ss, GMT)
        self.mtime_str = line[8]                # modification time (mm/dd/yy hh:mm:ss, GMT)
        self.atime_str = line[9]                # time of last access (mm/dd/yy hh:mm:ss, GMT)
        self.i_size = int(line[10])             # file size (decimal)
        self.i_blocks = int(line[11])           # number of (512 byte) blocks of disk space (decimal) taken up by this file
        
        if self.file_type != 's' or (self.i_size > 60):
            self.direct_blocks_num = [line[i] for i in range(12,23)] # block number for direct block
            self.ind_block_num = int(line[24])      # block number for indirect block
            self.dind_block_num = int(line[25])     # block number for doubly indirect block
            self.tind_block_num = int(line[26])     # block number for triply indirect block

class dirent:
    def __init__(self,line):
        self.parent_inode_num = int(line[1])    # parent inode number (decimal)
        self.byte_offset = int(line[2])         # logical byte offset (decimal) of this entry within the directory
        self.inode = int(line[3])               # inode number of the referenced file (decimal)
        self.rec_len = int(line[4])             # entry length (decimal)
        self.name_len = int(line[5])            # name length (decimal)
        self.name = line[6]                     # name, string, surrounded by single-quotes

class indirect:
    def __init__(self,line):
        self.owner_inode_num = int(line[1])     # I-node number of the owning file (decimal)
        self.level = int(line[2])               # (decimal) level of indirection for the block being scanned 
        self.logical_offset = int(line[3])      # logical block offset (decimal) represented by the referenced block. 
        self.ind_block_num = int(line[4])       # block number of the (1, 2, 3) indirect block being scanned (decimal) . . . not the highest level block (in the recursive scan)
        self.block_num = int(line[5])           # block number of the referenced block (decimal)




if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write("invalid arguments\n")
        sys.exit(1)

    try:
        csvfile=open(sys.argv[1], 'r')
    except IOError:
        sys.stderr.write("unable to open csv file\n")
        sys.exit(1)

    csv_reader = csv.reader(csvfile, delimiter=',')
    for line in csv_reader:
        if line[0] == "SUPERBLOCK":
            superblock(line)
        elif line[0] == "GROUP":
            group(line)
        elif line[0] == "BFREE":
            bfree.append(int(line[1]))
        elif line[0] == "IFREE":
            ifree.append(int(line[1]))
        elif line[0] == "INODE":
            inodes.append(inode(line))
        elif line[0] == "DIRENT":
            dir_entries.append(dirent(line))
        elif line[0] == "INDIRECT":
            indirect_blocks.append(indirect(line))
        else:
            sys.stderr.write("invalid csv file\n")
            sys.exit(1)
    