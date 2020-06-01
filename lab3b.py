#NAME: Mingchao Lian, Seoyoon Jin
#EMAIL: lianmccc@ucla.edu, seoyoonjin@g.ucla.edu
#ID: 005348062, 505297593

import sys, csv

bfree = [] # list of free blocks numbers
ifree = [] # list of free inode  numbers
inodes = [] # list of inodes
dir_entries = [] # list of dir entries
indirect_blocks = [] # list of indirect blocks

class SuperBlock:
    def __init__(self,line):
        self.s_blocks_count = int(line[1])      # total number of blocks 
        self.s_inodes_count = int(line[2])      # total number of i-nodes
        self.block_size = int(line[3])          # block size (in bytes, decimal)
        self.s_inode_size = int(line[4])        # i-node size (in bytes, decimal)
        self.s_blocks_per_group = int(line[5])  # blocks per group (decimal)
        self.s_inodes_per_group = int(line[6])  # i-nodes per group (decimal)
        self.s_first_ino = int(line[7])         # first non-reserved i-node (decimal)
        
class Group:
    def __init__(self,line):
        self.s_block_group_nr = int(line[1])            # group number (decimal, starting from zero)
        self.num_blocks_in_this_group = int(line[2])    # total number of blocks in this group (decimal)
        self.num_inodes_in_this_group = int(line[3])    # total number of i-nodes in this group (decimal)
        self.bg_free_blocks_count = int(line[4])        # number of free blocks (decimal)
        self.bg_free_inodes_count = int(line[5])        # number of free i-nodes (decimal)
        self.bg_block_bitmap = int(line[6])             # block number of free block bitmap for this group (decimal)
        self.bg_inode_bitmap = int(line[7])             # block number of free i-node bitmap for this group (decimal)
        self.bg_inode_table = int(line[8])              # block number of first block of i-nodes in this group (decimal)

class Inode:
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
        
        if self.has_ind():
            self.direct_blocks_num = [int(line[i]) for i in range(12,24)] # block numbers for direct block
            self.ind_block_num = int(line[24])      # block number for indirect block
            self.dind_block_num = int(line[25])     # block number for doubly indirect block
            self.tind_block_num = int(line[26])     # block number for triply indirect block

    def has_ind(self):
        """
        check if this inode has indirect blocks
        """
        return self.file_type != 's' or (self.i_size > 60)


class DirEnt:
    def __init__(self,line):
        self.parent_inode_num = int(line[1])    # parent inode number (decimal)
        self.byte_offset = int(line[2])         # logical byte offset (decimal) of this entry within the directory
        self.inode = int(line[3])               # inode number of the referenced file (decimal)
        self.rec_len = int(line[4])             # entry length (decimal)
        self.name_len = int(line[5])            # name length (decimal)
        self.name = line[6]                     # name, string, surrounded by single-quotes

class Indirect:
    def __init__(self,line):
        self.owner_inode_num = int(line[1])     # I-node number of the owning file (decimal)
        self.level = int(line[2])               # (decimal) level of indirection for the block being scanned 
        self.logical_offset = int(line[3])      # logical block offset (decimal) represented by the referenced block. 
        self.ind_block_num = int(line[4])       # block number of the (1, 2, 3) indirect block being scanned (decimal) . . . not the highest level block (in the recursive scan)
        self.block_num = int(line[5])           # block number of the referenced block (decimal)


#---------------------------------Block Consistency Audits---------------------------------
def print_invalid_block(block_num, block_level, inode_num, offset):
    print('INVALID {} {} IN INODE {} AT OFFSET {}'.format(block_level, block_num, inode_num, offset))

def print_reserved_block(block_num, block_level, inode_num, offset):
    print('RESERVED {} {} IN INODE {} AT OFFSET {}'.format(block_level, block_num, inode_num, offset))

def print_duplicate_block(block_num, block_level, inode_num, offset):
    print('DUPLICATE {} {} IN INODE {} AT OFFSET {}'.format(block_level, block_num, inode_num, offset))

def print_unreferenced_block(block_num):
    print('UNREFERENCED BLOCK {}'.format(block_num))

def print_allocated_block(block_num):
    print('ALLOCATED BLOCK {} ON FREELIST'.format(block_num))

def convert_block_level(block_level):
    if block_level == 0: 
        return 'BLOCK'
    elif block_level == 1:
        return'INDIRECT BLOCK'
    elif block_level == 2:
        return 'DOUBLE INDIRECT BLOCK'
    elif block_level == 3:
        return 'TRIPLE INDIRECT BLOCK'

def check_blocks():
    # Examine every single block pointer in every single I-node, direct block, indirect block, double-indirect block, and triple indirect block
    
    def block_offset(block_num):
        return 1024 + (block_num - 1) * superblock.block_size

    def block_invalid(block_num):
        # return true if block number is invalid, else return false
        return block_num < 0 or block_num > superblock.s_blocks_count
    
    def block_reserved(block_num):
        # return true if block number is reserved, else return false 
        first_legal_block_number = 5 + int(superblock.s_inodes_count * superblock.s_inode_size / superblock.block_size)
        return block_num < first_legal_block_number
            # block_num == group.bg_block_bitmap or \
            # block_num == group.bg_inode_bitmap or \
            # block_num == group.bg_inode_table or \
            

    def check_block(block_num, block_level, inode_num, offset):
        if block_num == 0: # no need to do anything if block_num is 0 
            return

        block_level = convert_block_level(block_level)
        # TODO: offset calculation

        if block_num in referenced:
            ref_info = referenced[block_num]
            ref_type = ref_info[0]
            ref_inode_num = ref_info[1]
            ref_offset = ref_info[2]
            duplicates.add((block_num, ref_type, ref_inode_num, ref_offset))
            duplicates.add((block_num, block_level, inode_num, offset))
        else:
            referenced[block_num] = (block_level, inode_num, offset)

        if block_invalid(block_num):
            print_invalid_block(block_num, block_level, inode_num, offset)

        if block_reserved(block_num):
            print_reserved_block(block_num, block_level, inode_num, offset)
        

    referenced = {}             # dictionary of referenced blocks. key: block number. value: touple of (block_level, inode number, offset)
    duplicates = set()          # set of duplicates. touples of (block_num, block_level, inode number, offset)

    num_blocks = int(superblock.block_size / 4) # number of block numbers in a block - used for calculating offset
    
    for inode in inodes:
        for idx, block_num in enumerate(inode.direct_blocks_num):
            offset = idx
            check_block(block_num, 0, inode.inode_num,  offset)
            
        
        if inode.has_ind():
            offset = 12
            check_block(inode.ind_block_num, 1, inode.inode_num, offset)

            offset = 12 + num_blocks
            check_block(inode.dind_block_num, 2, inode.inode_num, offset)

            offset = 12 + (num_blocks + 1) * num_blocks
            check_block(inode.tind_block_num, 3, inode.inode_num, offset)
            
    for indirect in indirect_blocks:
        block_num = indirect.block_num
        block_level = indirect.level - 1
        inode_num = indirect.owner_inode_num
        offset = indirect.logical_offset
        check_block(block_num, block_level, inode_num, offset)

    # print duplicates
    for duplicate in duplicates: 
        block_num, block_level, inode_num, offset = duplicate
        print_duplicate_block(block_num, block_level, inode_num, offset)
    
    unreferenced = set()
    for block_num in range(1, superblock.s_blocks_count):
        if block_num not in referenced and block_num not in bfree and not block_reserved(block_num):
            unreferenced.add(block_num)
    
    # print unreferenced
    for block_num in unreferenced:
        print_unreferenced_block(block_num)
    
    # print allocated
    for free_block_num in bfree:
        if free_block_num in referenced:
            print_allocated_block(free_block_num)

#---------------------------------Inode Consistency Audits---------------------------------
def print_allocated_inode(inode_num):
    print('ALLOCATED INODE {} ON FREELIST'.format(inode_num))

def print_unallocated_inode(inode_num):
    print('UNALLOCATED INODE {} NOT ON FREELIST'.format(inode_num))

def check_inodes():
    print('# TODO: check inodes')
    

#---------------------------------Directory Consistency Audits---------------------------------
 
# Incorrect link count (# of entries pointing to inode does not match inode link count)
def print_invalid_linkcount(inode_num, i_links_count, number_discovered):
    print('INODE {} HAS {} LINKS BUT LINKCOUNT IS {}'.format(inode_num, i_links_count, number_discovered))

# Unallocated (i_node referenced in entry is marked as free on bitmap)
def print_unallocated_dir_inode(parent_inode_num, name, inode):
    print('DIRECTORY INODE {} NAME \'{}\' INVALID INODE {}'.format(parent_inode_num, name, inode))

# Invalid (i_node # referenced in entry is invalid)
def print_invalid_dir_inode(parent_inode_num, name, inode):
    print('DIRECTORY INODE {} NAME \'{}\' UNALLOCATED INODE {}'.format(parent_inode_num, name, inode))

# . is not self
def print_self_invalid(parent_inode_num, inode):
    print('DIRECTORY INODE {} NAME \'..\' LINK TO INODE {} SHOULD BE {}'.format(parent_inode_num, inode, parent_inode_num))

# .. is not parent
def print_parent_invalid(parent_inode_num, inode):
    print('DIRECTORY INODE {} NAME \'.\' LINK TO INODE {} SHOULD BE {}'.format(parent_inode_num, inode, inode))
    


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
            superblock = SuperBlock(line)
        elif line[0] == "GROUP":
            group = Group(line)
        elif line[0] == "BFREE":
            bfree.append(int(line[1]))
        elif line[0] == "IFREE":
            ifree.append(int(line[1]))
        elif line[0] == "INODE":
            inodes.append(Inode(line))
        elif line[0] == "DIRENT":
            dir_entries.append(DirEnt(line))
        elif line[0] == "INDIRECT":
            indirect_blocks.append(Indirect(line))

        else:
            sys.stderr.write("invalid csv file\n")
            sys.exit(1)
    
    check_blocks()
    
