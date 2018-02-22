filename='update.test'
with open(filename) as f:
    conf=[]
    for line in f:
        line=line.strip().split(',')
        conf.append(line)
def update_data(d='d'):
    if 'test' in conf:
        print 'updated!!'
    else:
        print 'notupdate'
    
