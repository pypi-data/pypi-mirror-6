import struct
import os


#===================================================================================================
# CalculateHashForFile
#===================================================================================================
def CalculateHashForFile(name): 
    '''
    Calculates the hash for the given filename.
    
    Algorithm from: http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
    
    @param name: str
        Path to the file
        
    @return: str
        The calculated hash code, as an hex string.
    '''
    longlongformat = 'q'  # long long 
    bytesize = struct.calcsize(longlongformat) 
        
    f = open(name, "rb") 
        
    filesize = os.path.getsize(name) 
    hash = filesize 
        
    if filesize < 65536 * 2: 
        return "SizeError" 
     
    for x in range(65536/bytesize): 
        buffer = f.read(bytesize) 
        (l_value,)= struct.unpack(longlongformat, buffer)  
        hash += l_value 
        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
             

    f.seek(max(0,filesize-65536),0) 
    for x in range(65536/bytesize): 
        buffer = f.read(bytesize) 
        (l_value,)= struct.unpack(longlongformat, buffer)  
        hash += l_value 
        hash = hash & 0xFFFFFFFFFFFFFFFF 
     
    f.close() 
    returnedhash =  "%016x" % hash 
    return returnedhash