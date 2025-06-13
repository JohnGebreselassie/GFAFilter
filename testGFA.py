'''Testing program: Tests a file for complete links.'''

input = open("testOutput.gfa", "r")
storage = dict()
success = True
for line in input:
    new = line.split()

    '''Add all links to a dictionary.'''
    if line[0] == 'L':
        storage.setdefault(new[1], []).append(new[3])

        '''For each path, test if every pairing/link exists.'''
    elif line[0] == 'P':
        
        #initialize the newpath that is clear of + and ,
        rempath = line.replace('+', '')
        newpath = rempath.split(",")
        header = newpath[0][2:-2]
        newpath[0] = newpath[0][-1:] #newpath[0] was the header and the first node, so this line cuts out the header
        for i in range(0, int(len(newpath)-2)): #last index is *, so dont compare that one
            #compare the current index to the next one
            current = newpath[i]
            next = newpath[i+1]
            flag = False
            if next in storage[current]:
                #change the flag if the link exists
                flag = True
            if flag == False:
                #if the link doesn't exist, print the link 
                print("Error path: ",header, "links: ", current, next)
                success = False
                #break - if there are a lot of errors, you're gonna want to break after the first one, because there will be about 1 million errors.

if success == True:
    print("No errors found in any path")


input.close()



