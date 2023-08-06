import concurrent.futures

def jumble(func, iterable, max_workers = 50):
    jobs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers) as e:
        for i, item in enumerate(iterable):
            jobs[i] = e.submit(func, item)
        
        while len(jobs) > 0:
            for i in list(jobs.keys()):
                if jobs[i].done():
                    yield jobs[i]
                    del(jobs[i])
