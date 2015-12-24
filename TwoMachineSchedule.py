
def schedule(jobs):

    toleft  = []
    toright = []

    while len(jobs):

        leastjob     = None
        leastmachine = None
        leasttime    = 9999

        for k, v in jobs.items():
            for i in range(0,2):
                if v[i] < leasttime:
                    leastjob     = k
                    leastmachine = i
                    leasttime    = v[i]

        if leastmachine == 0: 
            toleft.append(leastjob)
        else:
            toright.insert(0,leastjob)

        jobs.pop(leastjob)
        print("least job: {0}, least machine: {1}, least time: {2}".format(leastjob, leastmachine+1, leasttime))

    return toleft + toright

JOBS = {1:(6,3), 2:(2,9), 3:(5,3), 4:(1,8), 5:(7,1), 6:(4,5), 7:(9,6)}
print(schedule(JOBS))


