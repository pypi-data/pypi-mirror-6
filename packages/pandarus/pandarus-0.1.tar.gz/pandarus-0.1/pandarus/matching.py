from .maps import Map, to_shape
from .projection import project, wgs84, MOLLWEIDE
from multiprocessing import Process, Queue, cpu_count
from pyproj import Proj
from shapely.geometry import shape
import itertools
import math
import progressbar
import time


def matchstick(status, output, from_map, from_objs, to_map, worker_id=None):
    """Multiprocessing worker for map matching"""
    if not from_objs:
        return

    # with open("matchstick.log", "a") as f:
    #     f.write("Worker id: %s\n\tfrom_map: %s\n\tto_map%s\n\tfrom_objs: %s\n" % (worker_id, from_map, to_map, from_objs)
    #     )

    results = {}
    to_map = Map(to_map)
    rtree_index = to_map.create_rtree_index()
    from_map = Map(from_map)

    projection_needed = (from_map.crs == to_map.crs) or \
        (Proj(wgs84(from_map.crs)).is_latlong() and \
         Proj(wgs84(to_map.crs)).is_latlong())

    if from_objs:
        from_gen = itertools.izip(from_objs, from_map.select(from_objs))
    else:
        from_gen = enumerate(from_map)

    for task_index, (from_index, from_obj) in enumerate(from_gen):
        geom = to_shape(from_obj['geometry'])

        if projection_needed:
            geom = project(geom, from_map.crs, to_map.crs)

        possibles = rtree_index.intersection(geom.bounds)
        for candidate_index in possibles:
            candidate = to_map[candidate_index]
            candidate_geom = to_shape(candidate['geometry'])
            if not geom.intersects(candidate_geom):
                continue

            intersection = geom.intersection(candidate_geom)
            if not intersection.area:
                continue

            results[from_index, candidate_index] = \
                project(intersection, to_map.crs, MOLLWEIDE).area

        if status:
            status.put((worker_id, (task_index, len(from_objs or []))))

        # with open("status.log", "a") as f:
        #     f.write("%s %s: %s/%s\n" % (time.asctime(), worker_id, task_index, len(from_objs)))

    output.put(results)
    # with open("status.log", "a") as f:
    #     f.write("%s %s: Finished\n" % (time.asctime(), worker_id))
    return


def matchmaker(from_map, to_map, from_objs=None, cpus=None, use_progressbar=True):
    # Monitoring code adapted from
    # http://stackoverflow.com/questions/13689927/how-to-get-the-amount-of-work-left-to-be-done-by-a-python-multiprocessing-pool
    status = Queue()
    results_queue = Queue()

    if from_objs:
        map_size = len(from_objs)
        ids = from_objs
    else:
        map_size = len(Map(from_map))
        ids = range(map_size)
    cpus = min(cpus or cpu_count(), map_size)

    chunk_size = int(math.ceil(map_size / float(cpus)))

    workers = []
    progress = {i: (0, 0) for i in xrange(cpus)}

    if use_progressbar:
        widgets = [
            'Features: ', progressbar.Percentage(), ' ',
            progressbar.Bar(marker=progressbar.RotatingMarker()), ' ',
            progressbar.ETA()
        ]
        pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=map_size
        ).start()

    for index, chunk in enumerate([ids[i * chunk_size:(i + 1) * chunk_size]
            for i in range(cpus)]):

        child = Process(
            target=matchstick,
            args=(status, results_queue, from_map, chunk, to_map, index)
        )
        workers.append(child)
        child.start()

    results=  {}

    while any(i.is_alive() for i in workers):
        time.sleep(0.1)
        # print "Workers:", sum([x.is_alive() for x in workers])
        # print "Exit codes:", set([x.exitcode for x in workers])
        while not status.empty():
            # Flush queue of progress reports
            worker, (completed, total) = status.get()
            progress[worker] = (completed, total)

        # Need to flush result queue or get weird multiprocessing errors
        # matchsticks finish but can't terminate correctly
        # see http://stackoverflow.com/questions/11854519/python-multiprocessing-some-functions-do-not-return-when-they-are-complete-que
        while not results_queue.empty():
            values = results_queue.get()
            if values:
                results.update(**values)

        if use_progressbar:
            pbar.update(sum([x[0] for x in progress.values()]))

    if use_progressbar:
        pbar.finish()

    while not results_queue.empty():
        values = results_queue.get()
        if values:
            results.update(**values)

    return results
