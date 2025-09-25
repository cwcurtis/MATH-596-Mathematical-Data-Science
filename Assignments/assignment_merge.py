import os
# We need to be able to pass in a directory and build an image list
def file_merger(directory1, directory2, depth):
    
    s1 = directory1
    s2 = directory2

    for root1, dirs1, files1 in os.walk(directory1):
        print(f"Current directory: {root}")
        print(f"  Subdirectories: {dirs}")
        print(f"  Files: {files}\n")        
    return None


base_directory = os.getcwd() # store your base directory for easy reference
dir1 = '/home/ccurtis/Downloads/Student_Assignments_Merged/Student_Assignments'
dir2 = '/home/ccurtis/Downloads/Student_Assignments_9_23/Student_Assignments'
file_merger(dir1, dir2)